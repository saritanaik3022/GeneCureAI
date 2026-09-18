"""
Bioinformatics nucleotide sequence utilities using Biopython standards.
"""
from typing import Tuple


def reverse_complement(sequence: str) -> str:
    """
    Returns reverse complement of a DNA sequence.
    """
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N',
                  'a': 't', 't': 'a', 'c': 'g', 'g': 'c', 'n': 'n'}
    return "".join(complement.get(base, 'N') for base in reversed(sequence))


def calculate_gc(sequence: str) -> float:
    """
    Computes GC percentage.
    """
    if not sequence:
        return 0.0
    seq = sequence.upper()
    gc = seq.count('G') + seq.count('C')
    return (gc / len(seq)) * 100.0
