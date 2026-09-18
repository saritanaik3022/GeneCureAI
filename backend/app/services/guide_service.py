"""
Stage 2: Guide RNA Identification Service.
"""
from typing import List, Dict, Any


class GuideService:
    """Service scanning forward and reverse-complement strands for candidate SpCas9 sgRNAs."""

    @staticmethod
    def calculate_gc_content(sequence: str) -> float:
        """Calculates GC percentage of a nucleotide sequence."""
        if not sequence:
            return 0.0
        seq = sequence.upper()
        gc_count = seq.count("G") + seq.count("C")
        return round((gc_count / len(seq)) * 100.0, 2)

    @staticmethod
    def has_poly_t(sequence: str) -> bool:
        """Checks for presence of TTTT Pol-III transcription terminator."""
        return "TTTT" in sequence.upper()
