"""
SpCas9 Dual-Strand PAM (5'-NGG-3') Scanner with Authentic 30-nt Genomic Context.
"""
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
from ..genome.fasta_reader import FASTAReader
from .models import CandidateGuideRNA
from .filters import GuideSequenceFilters


class SpCas9PAMScanner:
    """
    Scans genomic regions/exons for SpCas9 PAM (5'-NGG-3') motifs on both DNA strands,
    extracting 20-nt protospacers, 3-nt PAMs, and 30-nt contextual windows from GRCh38.
    """

    COMPLEMENT_MAP = str.maketrans("ACGTNacgtn", "TGCANtgcan")

    def __init__(self, fasta_reader: Optional[FASTAReader] = None, fasta_path: Optional[Path] = None):
        if fasta_reader is not None:
            self.fasta_reader: Optional[FASTAReader] = fasta_reader
        elif fasta_path is not None:
            self.fasta_reader = FASTAReader(fasta_path)
        else:
            self.fasta_reader = None

    @classmethod
    def reverse_complement(cls, sequence: str) -> str:
        return sequence.translate(cls.COMPLEMENT_MAP)[::-1]

    def scan_forward(
        self,
        sequence: str,
        exon_chrom_start: int = 1,
        gene_symbol: str = "CUSTOM",
        chromosome: str = "chr1",
        exon_number: Optional[int] = None
    ) -> List[CandidateGuideRNA]:
        """Scans in-memory sequence for forward strand SpCas9 (5'-NGG-3') PAM motifs."""
        seq = sequence.upper()
        n = len(seq)
        candidates: List[CandidateGuideRNA] = []

        for i in range(20, n - 2):
            pam = seq[i : i + 3]
            if pam[1:] == "GG" and set(pam).issubset(set("ACGT")):
                guide_seq = seq[i - 20 : i]
                if not set(guide_seq).issubset(set("ACGT")):
                    continue

                locus_start = exon_chrom_start + (i - 20)
                locus_end = locus_start + 22

                # 30-nt context
                ctx_start_idx = max(0, i - 24)
                ctx_end_idx = min(n, i + 6)
                context_30nt = seq[ctx_start_idx:ctx_end_idx].rjust(30, "N")[:30]

                cut_pos = locus_start + 16

                candidates.append(
                    CandidateGuideRNA(
                        candidate_id=f"gRNA-{gene_symbol}-{chromosome}-{locus_start}-F",
                        gene_symbol=gene_symbol,
                        gene_id="CUSTOM",
                        transcript_id="CUSTOM",
                        chromosome=chromosome,
                        strand="+",
                        protospacer_sequence=guide_seq,
                        pam_sequence=pam,
                        context_30nt_sequence=context_30nt,
                        genomic_start=locus_start,
                        genomic_end=locus_end,
                        exon_number=exon_number,
                        gc_percentage=GuideSequenceFilters.calculate_gc_percentage(guide_seq),
                        has_poly_t_terminator=GuideSequenceFilters.has_poly_t_terminator(guide_seq),
                        self_complementarity_score=GuideSequenceFilters.calculate_self_complementarity(guide_seq),
                        cleavage_coordinate=cut_pos,
                    )
                )
        return candidates

    def scan_reverse(
        self,
        sequence: str,
        exon_chrom_start: int = 1,
        gene_symbol: str = "CUSTOM",
        chromosome: str = "chr1",
        exon_number: Optional[int] = None
    ) -> List[CandidateGuideRNA]:
        """Scans in-memory sequence for reverse strand SpCas9 (CCN on reference) PAM motifs."""
        seq = sequence.upper()
        n = len(seq)
        candidates: List[CandidateGuideRNA] = []

        for i in range(0, n - 22):
            pam_rc = seq[i : i + 3]
            if pam_rc[:2] == "CC" and set(pam_rc).issubset(set("ACGT")):
                guide_ref = seq[i + 3 : i + 23]
                if not set(guide_ref).issubset(set("ACGT")):
                    continue

                guide_seq = self.reverse_complement(guide_ref)
                pam = self.reverse_complement(pam_rc)

                locus_start = exon_chrom_start + i
                locus_end = locus_start + 22

                # 30-nt context
                ctx_start_idx = max(0, i - 3)
                ctx_end_idx = min(n, i + 27)
                raw_ctx = seq[ctx_start_idx:ctx_end_idx]
                context_30nt = self.reverse_complement(raw_ctx).rjust(30, "N")[:30]

                cut_pos = locus_start + 5

                candidates.append(
                    CandidateGuideRNA(
                        candidate_id=f"gRNA-{gene_symbol}-{chromosome}-{locus_start}-R",
                        gene_symbol=gene_symbol,
                        gene_id="CUSTOM",
                        transcript_id="CUSTOM",
                        chromosome=chromosome,
                        strand="-",
                        protospacer_sequence=guide_seq,
                        pam_sequence=pam,
                        context_30nt_sequence=context_30nt,
                        genomic_start=locus_start,
                        genomic_end=locus_end,
                        exon_number=exon_number,
                        gc_percentage=GuideSequenceFilters.calculate_gc_percentage(guide_seq),
                        has_poly_t_terminator=GuideSequenceFilters.has_poly_t_terminator(guide_seq),
                        self_complementarity_score=GuideSequenceFilters.calculate_self_complementarity(guide_seq),
                        cleavage_coordinate=cut_pos,
                    )
                )
        return candidates

    def scan_genomic_interval(
        self,
        chromosome: str,
        interval_start: int,
        interval_end: int,
        gene_symbol: str = "UNKNOWN",
        gene_id: str = "UNKNOWN",
        transcript_id: str = "UNKNOWN",
        exon_number: Optional[int] = None,
        gc_min: float = 20.0,
        gc_max: float = 80.0,
        exclude_poly_t: bool = False
    ) -> List[CandidateGuideRNA]:
        """
        Scans a 1-based inclusive genomic interval [interval_start, interval_end] on GRCh38
        for SpCas9 PAM motifs (NGG on sense, CCN on antisense).
        """
        if self.fasta_reader is None:
            raise ValueError("FASTAReader is required for scan_genomic_interval.")

        chrom = self.fasta_reader.resolve_chromosome(chromosome)
        raw_interval_seq = self.fasta_reader.get_sequence(chrom, interval_start, interval_end).upper()
        interval_len = len(raw_interval_seq)

        candidates: List[CandidateGuideRNA] = []

        if interval_len < 23:
            return candidates

        # ----------------------------------------------------
        # 1. FORWARD STRAND SCAN (+) : 5'-[20nt guide][NGG PAM]-3'
        # ----------------------------------------------------
        for i in range(20, interval_len - 2):
            pam = raw_interval_seq[i : i + 3]
            if pam[1:] == "GG" and set(pam).issubset(set("ACGT")):
                guide_seq = raw_interval_seq[i - 20 : i]
                if not set(guide_seq).issubset(set("ACGT")):
                    continue

                locus_start = interval_start + (i - 20)
                locus_end = locus_start + 22 # 20 nt guide + 3 nt PAM = 23 bp total

                gc_pct = GuideSequenceFilters.calculate_gc_percentage(guide_seq)
                has_poly_t = GuideSequenceFilters.has_poly_t_terminator(guide_seq)
                self_comp = GuideSequenceFilters.calculate_self_complementarity(guide_seq)

                if gc_pct < gc_min or gc_pct > gc_max:
                    continue
                if exclude_poly_t and has_poly_t:
                    continue

                ctx_start = locus_start - 4
                ctx_end = locus_end + 3
                context_30nt = self.fasta_reader.get_sequence(chrom, ctx_start, ctx_end).upper()
                if len(context_30nt) != 30 or not set(context_30nt).issubset(set("ACGT")):
                    context_30nt = (raw_interval_seq[max(0, i - 24) : i + 6]).rjust(30, "N")[:30]

                cut_pos = locus_start + 16

                candidates.append(
                    CandidateGuideRNA(
                        candidate_id=f"gRNA-{gene_symbol}-{chrom}-{locus_start}-F",
                        gene_symbol=gene_symbol,
                        gene_id=gene_id,
                        transcript_id=transcript_id,
                        chromosome=chrom,
                        strand="+",
                        protospacer_sequence=guide_seq,
                        pam_sequence=pam,
                        context_30nt_sequence=context_30nt,
                        genomic_start=locus_start,
                        genomic_end=locus_end,
                        exon_number=exon_number,
                        gc_percentage=gc_pct,
                        has_poly_t_terminator=has_poly_t,
                        self_complementarity_score=self_comp,
                        cleavage_coordinate=cut_pos
                    )
                )

        # ----------------------------------------------------
        # 2. REVERSE STRAND SCAN (-) : 5'-[CCN PAM][20nt guide]-3' on reference
        # ----------------------------------------------------
        for i in range(0, interval_len - 22):
            pam_rc = raw_interval_seq[i : i + 3]
            if pam_rc[:2] == "CC" and set(pam_rc).issubset(set("ACGT")):
                guide_ref = raw_interval_seq[i + 3 : i + 23]
                if not set(guide_ref).issubset(set("ACGT")):
                    continue

                guide_seq = self.reverse_complement(guide_ref)
                pam = self.reverse_complement(pam_rc)

                locus_start = interval_start + i
                locus_end = locus_start + 22

                gc_pct = GuideSequenceFilters.calculate_gc_percentage(guide_seq)
                has_poly_t = GuideSequenceFilters.has_poly_t_terminator(guide_seq)
                self_comp = GuideSequenceFilters.calculate_self_complementarity(guide_seq)

                if gc_pct < gc_min or gc_pct > gc_max:
                    continue
                if exclude_poly_t and has_poly_t:
                    continue

                ctx_start = locus_start - 3
                ctx_end = locus_end + 4
                raw_ctx = self.fasta_reader.get_sequence(chrom, ctx_start, ctx_end).upper()
                context_30nt = self.reverse_complement(raw_ctx)
                if len(context_30nt) != 30 or not set(context_30nt).issubset(set("ACGT")):
                    context_30nt = (self.reverse_complement(raw_interval_seq[max(0, i - 3) : i + 27])).rjust(30, "N")[:30]

                cut_pos = locus_start + 5

                candidates.append(
                    CandidateGuideRNA(
                        candidate_id=f"gRNA-{gene_symbol}-{chrom}-{locus_start}-R",
                        gene_symbol=gene_symbol,
                        gene_id=gene_id,
                        transcript_id=transcript_id,
                        chromosome=chrom,
                        strand="-",
                        protospacer_sequence=guide_seq,
                        pam_sequence=pam,
                        context_30nt_sequence=context_30nt,
                        genomic_start=locus_start,
                        genomic_end=locus_end,
                        exon_number=exon_number,
                        gc_percentage=gc_pct,
                        has_poly_t_terminator=has_poly_t,
                        self_complementarity_score=self_comp,
                        cleavage_coordinate=cut_pos
                    )
                )

        return candidates
