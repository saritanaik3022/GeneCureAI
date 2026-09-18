"""
Real 105-Feature Vector Extraction Strategy for CRISPR sgRNA On-Target Activity.
Implements the genuine, deterministic gene-cure-v1-105 specification.
Contains zero fake values, zero zero-filled placeholder blocks, and strict biological definitions.
"""
from typing import List, Dict, Any, Union
import numpy as np
from ml.features.feature_schema import (
    FEATURE_VERSION,
    TOTAL_FEATURES,
    FEATURE_SCHEMA,
    FEATURE_NAMES,
)

# SantaLucia 1998 Unified DNA/DNA nearest-neighbor stacking free energy (deltaG 37 C, kcal/mol)
# Reference: SantaLucia J Jr. PNAS 1998 Feb 17;95(4):1460-5.
SANTALUCIA_NN_DELTA_G: Dict[str, float] = {
    "AA": -1.00, "TT": -1.00,
    "AT": -0.88,
    "TA": -0.58,
    "CA": -1.45, "TG": -1.45,
    "GT": -1.44, "AC": -1.44,
    "CT": -1.28, "AG": -1.28,
    "GA": -1.30, "TC": -1.30,
    "CG": -2.17,
    "GC": -2.24,
    "GG": -1.84, "CC": -1.84,
}

# Single-nucleotide 7 key positions in 30-mer context (0-indexed)
SINGLE_POSITIONS = [3, 4, 5, 19, 21, 22, 23]
BASES = ["A", "C", "G", "T"]

# 14 adjacent positional pairs in 30-mer context
DIMER_PAIRS = [
    (2, 3), (3, 4), (4, 5), (5, 6),
    (9, 10), (13, 14), (17, 18), (18, 19),
    (19, 20), (20, 21), (21, 22), (22, 23),
    (23, 24), (26, 27)
]

PURINES = {"A", "G"}
PYRIMIDINES = {"C", "T"}
STRONG_BASES = {"G", "C"}
WEAK_BASES = {"A", "T"}


def compute_nearest_neighbor_delta_g(seq: str) -> float:
    """Computes total nearest-neighbor stacking deltaG in kcal/mol for a DNA sequence."""
    total_dg = 0.0
    for i in range(len(seq) - 1):
        dinuc = seq[i:i+2].upper()
        total_dg += SANTALUCIA_NN_DELTA_G.get(dinuc, -1.20)
    return total_dg


class FeatureExtractor105:
    """
    Extracts fixed-length 105-dimensional numerical feature vector from a 30-nt context:
    4nt 5' flank + 20nt guide + 3nt PAM + 3nt 3' flank.
    """
    VERSION: str = FEATURE_VERSION
    FEATURE_NAMES: List[str] = FEATURE_NAMES
    TOTAL_FEATURES: int = TOTAL_FEATURES

    @classmethod
    def extract_features(cls, sequence_30nt: str) -> np.ndarray:
        """
        Extracts exactly 105 numerical features from a 30-nt context string.
        Returns a float32 1D numpy array of shape (105,).
        """
        seq = sequence_30nt.upper().strip()
        if len(seq) != 30:
            raise ValueError(f"Expected sequence length 30, got {len(seq)} for '{seq}'.")
        
        valid_dna = set("ACGT")
        if not set(seq).issubset(valid_dna):
            raise ValueError(f"Sequence contains invalid non-DNA characters: '{seq}'.")

        features = np.zeros(105, dtype=np.float32)
        idx = 0

        # -------------------------------------------------------------
        # 1. Single Nucleotide Positional Features (Indices 0..27, 28 features)
        # -------------------------------------------------------------
        for pos in SINGLE_POSITIONS:
            b = seq[pos]
            for target_base in BASES:
                features[idx] = 1.0 if b == target_base else 0.0
                idx += 1

        # -------------------------------------------------------------
        # 2. Dinucleotide Positional Interaction Features (Indices 28..83, 56 features)
        # -------------------------------------------------------------
        for p1, p2 in DIMER_PAIRS:
            b1 = seq[p1]
            b2 = seq[p2]
            
            # Metric 1: Purine-Purine (AA, AG, GA, GG)
            features[idx] = 1.0 if (b1 in PURINES and b2 in PURINES) else 0.0
            idx += 1
            
            # Metric 2: Pyrimidine-Pyrimidine (CC, CT, TC, TT)
            features[idx] = 1.0 if (b1 in PYRIMIDINES and b2 in PYRIMIDINES) else 0.0
            idx += 1
            
            # Metric 3: Strong GC Pair (GG, GC, CG, CC)
            features[idx] = 1.0 if (b1 in STRONG_BASES and b2 in STRONG_BASES) else 0.0
            idx += 1
            
            # Metric 4: Weak AT Pair (AA, AT, TA, TT)
            features[idx] = 1.0 if (b1 in WEAK_BASES and b2 in WEAK_BASES) else 0.0
            idx += 1

        # -------------------------------------------------------------
        # 3. GC Content Metrics (Indices 84..91, 8 features)
        # -------------------------------------------------------------
        flank_5p = seq[0:4]
        guide_20 = seq[4:24]
        seed_10 = guide_20[10:20]    # positions 14..23 in 30mer (proximal to PAM)
        distal_10 = guide_20[0:10]   # positions 4..13 in 30mer (distal from PAM)
        flank_3p = seq[27:30]

        gc_guide = (guide_20.count("G") + guide_20.count("C")) / 20.0
        gc_seed = (seed_10.count("G") + seed_10.count("C")) / 10.0
        gc_distal = (distal_10.count("G") + distal_10.count("C")) / 10.0
        gc_full_30 = (seq.count("G") + seq.count("C")) / 30.0
        gc_dev = abs(gc_guide - 0.50)
        gc_5p = (flank_5p.count("G") + flank_5p.count("C")) / 4.0
        gc_3p = (flank_3p.count("G") + flank_3p.count("C")) / 3.0
        gc_seed_distal_ratio = gc_seed / (gc_distal + 0.05)

        features[84] = gc_guide
        features[85] = gc_seed
        features[86] = gc_distal
        features[87] = gc_full_30
        features[88] = gc_dev
        features[89] = gc_5p
        features[90] = gc_3p
        features[91] = gc_seed_distal_ratio

        # -------------------------------------------------------------
        # 4. Thermodynamics & Nearest-Neighbor Stacking (Indices 92..99, 8 features)
        # -------------------------------------------------------------
        # Wallace Melting Temperatures: Tm = 2*(A+T) + 4*(G+C)
        tm_guide = 2.0 * (guide_20.count("A") + guide_20.count("T")) + 4.0 * (guide_20.count("G") + guide_20.count("C"))
        tm_seed = 2.0 * (seed_10.count("A") + seed_10.count("T")) + 4.0 * (seed_10.count("G") + seed_10.count("C"))
        tm_distal = 2.0 * (distal_10.count("A") + distal_10.count("T")) + 4.0 * (distal_10.count("G") + distal_10.count("C"))
        tm_full = 2.0 * (seq.count("A") + seq.count("T")) + 4.0 * (seq.count("G") + seq.count("C"))

        # SantaLucia 1998 Nearest-Neighbor deltaG (kcal/mol)
        dg_seed = compute_nearest_neighbor_delta_g(seed_10)
        dg_distal = compute_nearest_neighbor_delta_g(distal_10)
        dg_guide = compute_nearest_neighbor_delta_g(guide_20)
        thermo_asymmetry = dg_seed - dg_distal

        features[92] = tm_guide
        features[93] = tm_seed
        features[94] = tm_distal
        features[95] = tm_full
        features[96] = dg_seed
        features[97] = dg_distal
        features[98] = dg_guide
        features[99] = thermo_asymmetry

        # -------------------------------------------------------------
        # 5. Sequence Complexity & Motifs (Indices 100..104, 5 features)
        # -------------------------------------------------------------
        features[100] = 1.0 if "TTTT" in seq else 0.0
        features[101] = 1.0 if "GGGG" in seq else 0.0
        features[102] = 1.0 if "CCCC" in seq else 0.0
        features[103] = 1.0 if "AAAA" in seq else 0.0
        features[104] = 1.0 if "GG" in guide_20[18:20] else 0.0

        assert len(features) == 105, f"Expected 105 features, got {len(features)}"
        return features

    @classmethod
    def extract_matrix(cls, sequences: List[str]) -> np.ndarray:
        """
        Extracts an (N, 105) feature matrix from a list of N 30-nt context sequences.
        """
        matrix = np.zeros((len(sequences), 105), dtype=np.float32)
        for i, seq in enumerate(sequences):
            matrix[i] = cls.extract_features(seq)
        return matrix
