"""
One-hot sequence encodings and numerical feature normalizers.
"""
import numpy as np


def one_hot_encode_sequence(sequence: str) -> np.ndarray:
    """
    Encodes nucleotide sequence of length L into (4, L) one-hot binary matrix [A, C, G, T].
    """
    mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    seq_upper = sequence.upper()
    encoding = np.zeros((4, len(seq_upper)), dtype=np.float32)
    for i, base in enumerate(seq_upper):
        if base in mapping:
            encoding[mapping[base], i] = 1.0
    return encoding
