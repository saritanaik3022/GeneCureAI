"""
GRCh38 Reference Genome Sequence Extractor with Exon Provenance and CDS Integrity Validation.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import os
from .gene_lookup import SelectedGeneTranscript
from ..genome.fasta_reader import FASTAReader


@dataclass
class ExonSequenceRecord:
    exon_number: int
    chromosome: str
    start: int
    end: int
    strand: str
    length: int
    sequence: str


@dataclass
class ExtractedGeneSequence:
    gene_symbol: str
    gene_id: str
    transcript_id: str
    chromosome: str
    strand: str
    reference_assembly: str
    annotation_source: str
    cds_sequence: str
    full_transcript_sequence: str
    genomic_locus_sequence: str
    cds_length: int
    transcript_length: int
    genomic_length: int
    exon_records: List[ExonSequenceRecord]
    is_cds_valid: bool
    validation_notes: List[str]


class FASTASequenceExtractor:
    """
    Extracts authentic sequences from GRCh38 reference FASTA for transcripts and exons.
    """

    def __init__(self, fasta_path: Path):
        self.fasta_reader = FASTAReader(fasta_path)

    def extract_genomic_region(self, chrom: str, start: int, end: int, strand: str = "+") -> str:
        """
        Extracts 1-based inclusive genomic interval [start, end].
        If strand is '-', returns reverse complement.
        """
        seq = self.fasta_reader.get_sequence(chrom, start, end)
        if strand == "-":
            return self.fasta_reader.reverse_complement(seq)
        return seq

    def extract_spliced_sequence(
        self, chrom: str, exon_intervals: List[Dict[str, Any]], strand: str
    ) -> Tuple[str, List[ExonSequenceRecord]]:
        """
        Extracts and splices exons in biological 5' -> 3' transcription orientation.
        Returns the spliced sequence and individual exon records with provenance.
        """
        # Sort exons by genomic start
        exons_sorted = sorted(exon_intervals, key=lambda e: e["start"])

        # If on negative strand, transcription proceeds from highest genomic position to lowest
        if strand == "-":
            exons_sorted = list(reversed(exons_sorted))

        spliced_parts = []
        exon_records = []

        for item in exons_sorted:
            start = item["start"]
            end = item["end"]
            exon_num = item.get("exon_number", len(exon_records) + 1)
            raw_seq = self.fasta_reader.get_sequence(chrom, start, end)
            oriented_seq = self.fasta_reader.reverse_complement(raw_seq) if strand == "-" else raw_seq

            spliced_parts.append(oriented_seq)
            exon_records.append(
                ExonSequenceRecord(
                    exon_number=exon_num,
                    chromosome=chrom,
                    start=start,
                    end=end,
                    strand=strand,
                    length=len(oriented_seq),
                    sequence=oriented_seq
                )
            )

        return "".join(spliced_parts), exon_records

    def validate_coding_sequence(self, cds_seq: str) -> Tuple[bool, List[str]]:
        """
        Validates coding sequence integrity:
        1. Non-empty
        2. Valid IUPAC DNA (A, C, G, T)
        3. Length divisible by 3 (in-frame)
        4. Standard start codon (ATG)
        5. Standard stop codon (TAA, TAG, TGA)
        6. Absence of internal premature stop codons
        """
        notes = []
        is_valid = True

        if not cds_seq:
            return False, ["CDS sequence is empty."]

        # Check nucleotide characters
        invalid_bases = set(cds_seq.upper()) - set("ACGT")
        if invalid_bases:
            is_valid = False
            notes.append(f"Non-canonical DNA bases detected: {invalid_bases}")

        # Frame length check
        if len(cds_seq) % 3 != 0:
            is_valid = False
            notes.append(f"CDS length ({len(cds_seq)} bp) is not divisible by 3 (frame offset = {len(cds_seq) % 3}).")

        # Start codon check
        start_codon = cds_seq[:3].upper()
        if start_codon != "ATG":
            notes.append(f"Non-canonical start codon: {start_codon} (expected ATG).")

        # Stop codon check
        stop_codon = cds_seq[-3:].upper()
        valid_stops = {"TAA", "TAG", "TGA"}
        if stop_codon not in valid_stops:
            notes.append(f"Non-canonical stop codon: {stop_codon} (expected TAA/TAG/TGA).")

        # Premature stop codon scan
        internal_stops = []
        for i in range(0, len(cds_seq) - 3, 3):
            codon = cds_seq[i:i+3].upper()
            if codon in valid_stops:
                internal_stops.append((i // 3 + 1, codon))

        if internal_stops:
            is_valid = False
            notes.append(f"Premature internal stop codons detected at codon positions: {internal_stops}")

        if not notes:
            notes.append("Canonical full-length coding sequence (ATG start, valid stop, in-frame, no internal stops).")

        return is_valid, notes

    def extract_gene_sequence(self, gene_transcript: SelectedGeneTranscript) -> ExtractedGeneSequence:
        """
        Extracts genomic locus, spliced mature transcript, and CDS sequences for a gene.
        """
        chrom = gene_transcript.chromosome
        strand = gene_transcript.strand

        # 1. Genomic locus sequence
        genomic_seq = self.extract_genomic_region(
            chrom, gene_transcript.genomic_start, gene_transcript.genomic_end, strand=strand
        )

        # 2. Spliced mature transcript
        full_transcript_seq, exon_records = self.extract_spliced_sequence(
            chrom, gene_transcript.exons, strand=strand
        )

        # 3. Coding Sequence (CDS)
        if gene_transcript.cds_exons:
            cds_seq, cds_records = self.extract_spliced_sequence(
                chrom, gene_transcript.cds_exons, strand=strand
            )
        else:
            cds_seq = full_transcript_seq
            cds_records = exon_records

        is_valid, validation_notes = self.validate_coding_sequence(cds_seq)

        return ExtractedGeneSequence(
            gene_symbol=gene_transcript.gene_symbol,
            gene_id=gene_transcript.gene_id,
            transcript_id=gene_transcript.transcript_id,
            chromosome=chrom,
            strand=strand,
            reference_assembly=gene_transcript.reference_assembly,
            annotation_source=gene_transcript.annotation_source,
            cds_sequence=cds_seq,
            full_transcript_sequence=full_transcript_seq,
            genomic_locus_sequence=genomic_seq,
            cds_length=len(cds_seq),
            transcript_length=len(full_transcript_seq),
            genomic_length=len(genomic_seq),
            exon_records=exon_records,
            is_cds_valid=is_valid,
            validation_notes=validation_notes
        )
