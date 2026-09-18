"""
Candidate Guide RNA Generation Orchestrator for Target Cancer Genes.
"""
from typing import List, Dict, Optional, Any
from pathlib import Path
from ..gene_selection.gene_lookup import GeneLookup, SelectedGeneTranscript
from ..gene_selection.gtf_parser import GTFParser
from ..genome.fasta_reader import FASTAReader
from .pam_scanner import SpCas9PAMScanner
from .models import CandidateGuideRNA, GuideDesignScanResult


class CandidateGenerator:
    """
    Coordinates gene lookup, exon extraction, and dual-strand SpCas9 PAM scanning.
    """

    def __init__(
        self,
        gtf_path: Optional[Path] = None,
        fasta_path: Optional[Path] = None,
        gtf_parser: Optional[GTFParser] = None,
        fasta_reader: Optional[FASTAReader] = None
    ):
        try:
            from app.core.config import settings
            default_gtf = Path(settings.GENCODE_GTF)
            default_fasta = Path(settings.GENOME_FASTA)
        except Exception:
            base_dir = Path(__file__).resolve().parent.parent.parent
            default_gtf = base_dir / "data" / "annotation" / "gencode.v46.annotation.gtf"
            default_fasta = base_dir / "data" / "genome" / "GRCh38.primary_assembly.genome.fa"

        resolved_gtf = gtf_path or default_gtf
        resolved_fasta = fasta_path or default_fasta

        self.gtf_parser = gtf_parser or GTFParser(resolved_gtf)
        self.fasta_reader = fasta_reader or FASTAReader(resolved_fasta)
        self.gene_lookup = GeneLookup(gtf_parser=self.gtf_parser)
        self.pam_scanner = SpCas9PAMScanner(fasta_reader=self.fasta_reader)

    def scan_gene_exons(
        self,
        gene_symbol: str,
        gc_min: float = 20.0,
        gc_max: float = 80.0,
        exclude_poly_t: bool = True
    ) -> GuideDesignScanResult:
        """
        Scans all annotated coding exons (CDS) of the canonical transcript for the target gene.
        """
        gene_details = self.gene_lookup.get_gene_details(gene_symbol)

        all_candidates: List[CandidateGuideRNA] = []
        seen_coordinates: set = set()

        # Target exons to scan: prefer CDS exons, fallback to mature exons
        exons_to_scan = gene_details.cds_exons if gene_details.cds_exons else gene_details.exons

        for exon in exons_to_scan:
            exon_candidates = self.pam_scanner.scan_genomic_interval(
                chromosome=gene_details.chromosome,
                interval_start=exon["start"],
                interval_end=exon["end"],
                gene_symbol=gene_details.gene_symbol,
                gene_id=gene_details.gene_id,
                transcript_id=gene_details.transcript_id,
                exon_number=exon["exon_number"],
                gc_min=gc_min,
                gc_max=gc_max,
                exclude_poly_t=exclude_poly_t
            )

            for cand in exon_candidates:
                coord_key = (cand.chromosome, cand.genomic_start, cand.genomic_end, cand.strand)
                if coord_key not in seen_coordinates:
                    seen_coordinates.add(coord_key)
                    all_candidates.append(cand)

        # Sort candidates deterministically by genomic start coordinate
        all_candidates.sort(key=lambda c: (c.genomic_start, c.strand))

        # Assign clean human-readable sequential candidate IDs
        for idx, cand in enumerate(all_candidates, start=1):
            cand.candidate_id = f"gRNA-{gene_details.gene_symbol}-{idx:04d}"

        return GuideDesignScanResult(
            gene_symbol=gene_details.gene_symbol,
            gene_id=gene_details.gene_id,
            transcript_id=gene_details.transcript_id,
            chromosome=gene_details.chromosome,
            strand=gene_details.strand,
            reference_assembly="GRCh38",
            annotation_source="GENCODE v46",
            total_candidates_identified=len(all_candidates),
            total_exons_scanned=len(exons_to_scan),
            cds_length_scanned=gene_details.total_cds_length,
            execution_mode="REAL_MODE",
            candidates=all_candidates,
            filter_summary={
                "gc_min": int(gc_min),
                "gc_max": int(gc_max),
                "exclude_poly_t": int(exclude_poly_t)
            }
        )

    def generate_candidates_for_gene(
        self,
        gene_symbol: str,
        gc_min: float = 20.0,
        gc_max: float = 80.0,
        exclude_poly_t: bool = True
    ) -> GuideDesignScanResult:
        """Alias for scan_gene_exons."""
        return self.scan_gene_exons(
            gene_symbol=gene_symbol,
            gc_min=gc_min,
            gc_max=gc_max,
            exclude_poly_t=exclude_poly_t
        )
