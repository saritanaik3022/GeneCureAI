"""
GENCODE GTF Parser for Gene, Transcript, Exon, and CDS Feature Extraction.
Ultra-high performance single-pass parser with O(1) string matching.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import os
import re


@dataclass
class ExonFeature:
    exon_number: int
    start: int
    end: int
    strand: str
    length: int = field(init=False)

    def __post_init__(self):
        self.length = self.end - self.start + 1


@dataclass
class TranscriptFeature:
    transcript_id: str
    transcript_name: str
    transcript_type: str
    chromosome: str
    start: int
    end: int
    strand: str
    tags: List[str] = field(default_factory=list)
    support_level: Optional[int] = None
    appris_level: Optional[str] = None
    exons: List[ExonFeature] = field(default_factory=list)
    cds_exons: List[ExonFeature] = field(default_factory=list)

    @property
    def total_exon_length(self) -> int:
        return sum(e.length for e in self.exons)

    @property
    def total_cds_length(self) -> int:
        return sum(c.length for c in self.cds_exons)

    @property
    def is_canonical(self) -> bool:
        return "Ensembl_canonical" in self.tags or "MANE_Select" in self.tags

    @property
    def is_appris_principal(self) -> bool:
        return any("appris_principal" in tag for tag in self.tags) or bool(self.appris_level and "principal" in self.appris_level)


@dataclass
class GeneFeature:
    gene_id: str
    gene_name: str
    gene_type: str
    chromosome: str
    start: int
    end: int
    strand: str
    transcripts: Dict[str, TranscriptFeature] = field(default_factory=dict)


class GTFParser:
    """
    Parser for GENCODE GTF files with fast target-filtering and in-memory caching.
    """

    GENE_ALIASES: Dict[str, str] = {
        "HER2": "ERBB2",
        "ERBB2": "ERBB2",
        "P53": "TP53",
        "BETA-CATENIN": "CTNNB1",
    }

    _GENE_NAME_RE = re.compile(r'gene_name "([^"]+)"')
    _GENE_ID_RE = re.compile(r'gene_id "([^"]+)"')
    _TX_ID_RE = re.compile(r'transcript_id "([^"]+)"')
    _TX_NAME_RE = re.compile(r'transcript_name "([^"]+)"')
    _TX_TYPE_RE = re.compile(r'transcript_type "([^"]+)"')
    _GENE_TYPE_RE = re.compile(r'gene_type "([^"]+)"')
    _EXON_NUM_RE = re.compile(r'exon_number (\d+)')
    _TSL_RE = re.compile(r'transcript_support_level (\d+)')
    _TAG_RE = re.compile(r'tag "([^"]+)"')

    def __init__(self, gtf_path: Path):
        self.gtf_path = Path(gtf_path)
        self._parsed_genes: Dict[str, GeneFeature] = {}

    @classmethod
    def normalize_symbol(cls, symbol: str) -> str:
        s_upper = symbol.strip().upper()
        return cls.GENE_ALIASES.get(s_upper, s_upper)

    def extract_genes(self, target_symbols: Set[str]) -> Dict[str, GeneFeature]:
        """
        Extracts gene, transcript, exon, and CDS records for the requested target gene symbols.
        Uses single-pass high-throughput filtering.
        """
        norm_targets = {self.normalize_symbol(s) for s in target_symbols}

        # Check if all targets are already cached
        if all(t in self._parsed_genes for t in norm_targets):
            return {t: self._parsed_genes[t] for t in norm_targets if t in self._parsed_genes}

        if not self.gtf_path.exists():
            raise FileNotFoundError(f"GENCODE GTF file not found at: {self.gtf_path}")

        genes: Dict[str, GeneFeature] = {}
        gene_id_to_norm_name: Dict[str, str] = {}

        # Exact target match patterns
        exact_gene_patterns = {f'gene_name "{t}"': t for t in norm_targets}

        with open(self.gtf_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    continue

                # Fast check: does this line have any target pattern?
                matched_target = None
                for pat, sym in exact_gene_patterns.items():
                    if pat in line:
                        matched_target = sym
                        break

                if not matched_target:
                    # check if gene_id was previously identified
                    for gid, sym in gene_id_to_norm_name.items():
                        if gid in line:
                            matched_target = sym
                            break

                if not matched_target:
                    continue

                parts = line.strip().split("\t")
                if len(parts) < 9:
                    continue

                chrom, _, feature, start_str, end_str, _, strand, _, attr_str = parts
                start, end = int(start_str), int(end_str)

                # Extract attributes via regex
                gname_m = self._GENE_NAME_RE.search(attr_str)
                gene_name = gname_m.group(1) if gname_m else matched_target
                norm_name = self.normalize_symbol(gene_name)

                if norm_name not in norm_targets:
                    continue

                gid_m = self._GENE_ID_RE.search(attr_str)
                gene_id = gid_m.group(1) if gid_m else f"GENE_{norm_name}"

                if gene_id and gene_id not in gene_id_to_norm_name:
                    gene_id_to_norm_name[gene_id] = norm_name

                if norm_name not in genes:
                    gtype_m = self._GENE_TYPE_RE.search(attr_str)
                    genes[norm_name] = GeneFeature(
                        gene_id=gene_id,
                        gene_name=norm_name,
                        gene_type=gtype_m.group(1) if gtype_m else "protein_coding",
                        chromosome=chrom,
                        start=start,
                        end=end,
                        strand=strand
                    )

                gene_obj = genes[norm_name]
                if feature == "gene":
                    gene_obj.start = start
                    gene_obj.end = end
                    gene_obj.chromosome = chrom
                    gene_obj.strand = strand
                    gene_obj.gene_id = gene_id

                tx_m = self._TX_ID_RE.search(attr_str)
                if not tx_m:
                    continue

                transcript_id = tx_m.group(1)
                if transcript_id not in gene_obj.transcripts:
                    txname_m = self._TX_NAME_RE.search(attr_str)
                    txtype_m = self._TX_TYPE_RE.search(attr_str)
                    tsl_m = self._TSL_RE.search(attr_str)
                    tags = self._TAG_RE.findall(attr_str)

                    support_lvl = int(tsl_m.group(1)) if tsl_m else None
                    appris = next((t for t in tags if "appris" in t), None)

                    gene_obj.transcripts[transcript_id] = TranscriptFeature(
                        transcript_id=transcript_id,
                        transcript_name=txname_m.group(1) if txname_m else transcript_id,
                        transcript_type=txtype_m.group(1) if txtype_m else "protein_coding",
                        chromosome=chrom,
                        start=start,
                        end=end,
                        strand=strand,
                        tags=tags,
                        support_level=support_lvl,
                        appris_level=appris
                    )

                tx_obj = gene_obj.transcripts[transcript_id]
                exon_m = self._EXON_NUM_RE.search(attr_str)

                if feature == "exon":
                    exon_num = int(exon_m.group(1)) if exon_m else (len(tx_obj.exons) + 1)
                    tx_obj.exons.append(ExonFeature(
                        exon_number=exon_num,
                        start=start,
                        end=end,
                        strand=strand
                    ))
                elif feature == "CDS":
                    exon_num = int(exon_m.group(1)) if exon_m else (len(tx_obj.cds_exons) + 1)
                    tx_obj.cds_exons.append(ExonFeature(
                        exon_number=exon_num,
                        start=start,
                        end=end,
                        strand=strand
                    ))

        # Sort exons by genomic coordinates
        for gene in genes.values():
            for tx in gene.transcripts.values():
                tx.exons.sort(key=lambda e: e.start)
                tx.cds_exons.sort(key=lambda e: e.start)

        self._parsed_genes.update(genes)
        return genes
