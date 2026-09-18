"""
Gene and Transcript Lookup Engine with Configurable Multi-Tier Selection Policy.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from .gtf_parser import GTFParser, GeneFeature, TranscriptFeature


@dataclass
class SelectedGeneTranscript:
    gene_symbol: str
    gene_id: str
    cancer_types: List[str]
    chromosome: str
    strand: str
    genomic_start: int
    genomic_end: int
    transcript_id: str
    transcript_name: str
    selection_policy: str
    total_transcripts_evaluated: int
    exon_count: int
    cds_exon_count: int
    total_exon_length: int
    total_cds_length: int
    exons: List[Dict[str, Any]]
    cds_exons: List[Dict[str, Any]]
    reference_assembly: str = "GRCh38"
    annotation_source: str = "GENCODE v46"


class GeneLookup:
    """
    Lookup service for cancer-related genes with policy-driven transcript resolution.
    """

    DEFAULT_TARGET_GENES: Dict[str, Dict[str, Any]] = {
        "BRCA1": {"cancer_types": ["Breast cancer"], "aliases": ["BRCA1"]},
        "HER2": {"cancer_types": ["Breast cancer"], "aliases": ["ERBB2", "HER2", "NEU"]},
        "TP53": {"cancer_types": ["Breast cancer", "Lung cancer", "Liver cancer"], "aliases": ["TP53", "P53"]},
        "EGFR": {"cancer_types": ["Lung cancer"], "aliases": ["EGFR", "ERBB1"]},
        "KRAS": {"cancer_types": ["Lung cancer"], "aliases": ["KRAS", "KRAS2"]},
        "ALK": {"cancer_types": ["Lung cancer"], "aliases": ["ALK"]},
        "CTNNB1": {"cancer_types": ["Liver cancer"], "aliases": ["CTNNB1", "beta-catenin"]},
        "AXIN1": {"cancer_types": ["Liver cancer"], "aliases": ["AXIN1"]},
        "TERT": {"cancer_types": ["Liver cancer"], "aliases": ["TERT", "EST2"]}
    }

    def __init__(self, gtf_path: Optional[Path] = None, gtf_parser: Optional[GTFParser] = None):
        if gtf_parser is not None:
            self.gtf_parser = gtf_parser
        elif gtf_path is not None:
            self.gtf_parser = GTFParser(gtf_path)
        else:
            raise ValueError("Either gtf_path or gtf_parser must be provided.")
        self._cached_genes: Optional[Dict[str, GeneFeature]] = None

    def _ensure_loaded(self):
        if self._cached_genes is None:
            target_symbols = set(self.DEFAULT_TARGET_GENES.keys())
            for gene_meta in self.DEFAULT_TARGET_GENES.values():
                target_symbols.update(gene_meta["aliases"])
            self._cached_genes = self.gtf_parser.extract_genes(target_symbols)

    def select_canonical_transcript(self, gene: GeneFeature) -> Tuple[TranscriptFeature, str]:
        """
        Deterministic multi-tier transcript selection policy:
        1. Tier 1: MANE_Select / Ensembl_canonical tagged + APPRIS principal + protein_coding.
        2. Tier 2: MANE_Select / Ensembl_canonical tagged + protein_coding.
        3. Tier 3: APPRIS principal tagged + protein_coding.
        4. Tier 4: Protein coding with lowest Transcript Support Level (TSL 1).
        5. Tier 5: Longest Coding Sequence (CDS) length.
        6. Tier 6: Longest mature exonic length.
        """
        transcripts = list(gene.transcripts.values())
        if not transcripts:
            raise ValueError(f"No transcripts found for gene {gene.gene_name}")

        # Filter protein coding transcripts
        coding_transcripts = [t for t in transcripts if t.transcript_type == "protein_coding"]
        candidates_pool = coding_transcripts if coding_transcripts else transcripts

        # Tier 1: Canonical AND APPRIS Principal
        tier1 = [t for t in candidates_pool if t.is_canonical and t.is_appris_principal]
        if tier1:
            tier1.sort(key=lambda t: (t.total_cds_length, t.total_exon_length), reverse=True)
            chosen = tier1[0]
            reason = f"MANE Select/Ensembl Canonical + APPRIS Principal ({chosen.appris_level or 'principal'}); CDS={chosen.total_cds_length} bp"
            return chosen, reason

        # Tier 2: Canonical (MANE_Select or Ensembl_canonical)
        tier2 = [t for t in candidates_pool if t.is_canonical]
        if tier2:
            tier2.sort(key=lambda t: (t.total_cds_length, t.total_exon_length), reverse=True)
            chosen = tier2[0]
            tags_str = ", ".join([t for t in chosen.tags if "canonical" in t.lower() or "mane" in t.lower()]) or "Canonical"
            reason = f"Tagged as {tags_str}; protein_coding; CDS={chosen.total_cds_length} bp"
            return chosen, reason

        # Tier 3: APPRIS Principal
        tier3 = [t for t in candidates_pool if t.is_appris_principal]
        if tier3:
            tier3.sort(key=lambda t: (t.total_cds_length, t.total_exon_length), reverse=True)
            chosen = tier3[0]
            reason = f"APPRIS Principal ({chosen.appris_level or 'principal'}); protein_coding; CDS={chosen.total_cds_length} bp"
            return chosen, reason

        # Tier 4: TSL 1
        tier4 = [t for t in candidates_pool if t.support_level == 1]
        if tier4:
            tier4.sort(key=lambda t: (t.total_cds_length, t.total_exon_length), reverse=True)
            chosen = tier4[0]
            reason = f"Transcript Support Level 1 (TSL=1); protein_coding; CDS={chosen.total_cds_length} bp"
            return chosen, reason

        # Tier 5: Longest CDS
        candidates_pool.sort(key=lambda t: (t.total_cds_length, t.total_exon_length), reverse=True)
        chosen = candidates_pool[0]
        reason = f"Longest CDS in available transcripts; CDS={chosen.total_cds_length} bp, Exons={chosen.total_exon_length} bp"
        return chosen, reason

    def get_gene_details(self, symbol: str) -> SelectedGeneTranscript:
        """Resolves target gene and extracts selected canonical transcript with exon coordinates."""
        self._ensure_loaded()
        norm_symbol = self.gtf_parser.normalize_symbol(symbol)

        meta_key = None
        for k, v in self.DEFAULT_TARGET_GENES.items():
            if k.upper() == symbol.strip().upper() or norm_symbol in [a.upper() for a in v["aliases"]]:
                meta_key = k
                break

        if not meta_key:
            meta_key = norm_symbol

        gene_obj = self._cached_genes.get(norm_symbol)
        if not gene_obj:
            raise KeyError(f"Gene '{symbol}' (normalized: '{norm_symbol}') not found in GENCODE annotation.")

        selected_tx, policy_reason = self.select_canonical_transcript(gene_obj)
        cancer_types = self.DEFAULT_TARGET_GENES.get(meta_key, {}).get("cancer_types", ["Pan-cancer"])

        exons_data = [
            {"exon_number": e.exon_number, "start": e.start, "end": e.end, "length": e.length, "strand": e.strand}
            for e in selected_tx.exons
        ]
        cds_data = [
            {"exon_number": c.exon_number, "start": c.start, "end": c.end, "length": c.length, "strand": c.strand}
            for c in selected_tx.cds_exons
        ]

        return SelectedGeneTranscript(
            gene_symbol=meta_key,
            gene_id=gene_obj.gene_id,
            cancer_types=cancer_types,
            chromosome=gene_obj.chromosome,
            strand=gene_obj.strand,
            genomic_start=gene_obj.start,
            genomic_end=gene_obj.end,
            transcript_id=selected_tx.transcript_id,
            transcript_name=selected_tx.transcript_name,
            selection_policy=policy_reason,
            total_transcripts_evaluated=len(gene_obj.transcripts),
            exon_count=len(selected_tx.exons),
            cds_exon_count=len(selected_tx.cds_exons),
            total_exon_length=selected_tx.total_exon_length,
            total_cds_length=selected_tx.total_cds_length,
            exons=exons_data,
            cds_exons=cds_data,
            reference_assembly="GRCh38",
            annotation_source="GENCODE v46"
        )

    def get_all_target_genes(self) -> List[SelectedGeneTranscript]:
        """Returns resolved metadata for all 9 curated cancer target genes."""
        results = []
        for symbol in self.DEFAULT_TARGET_GENES.keys():
            results.append(self.get_gene_details(symbol))
        return results
