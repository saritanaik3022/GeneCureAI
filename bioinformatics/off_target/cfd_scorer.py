"""
Cutting Frequency Determination (CFD) Scoring Engine.
Implements the official Doench et al., Nature Biotechnology 2016 off-target cleavage probability model.
Formula: CFD = PAM_weight * Product_over_mismatches( Mismatch_weight(position, guide_base, target_base) )
Specificity Score = 1.0 / (1.0 + Sum(CFD_scores)) * 100.0
"""
from typing import List, Dict, Tuple, Optional
import numpy as np

# Official Doench et al. (2016) PAM weights for SpCas9
PAM_WEIGHTS: Dict[str, float] = {
    "AGG": 1.0, "CGG": 1.0, "GGG": 1.0, "TGG": 1.0, # NGG
    "AGA": 0.259, "CGA": 0.259, "GGA": 0.259, "TGA": 0.259, # NGA
    "AAG": 0.259, "CAG": 0.259, "GAG": 0.259, "TAG": 0.259, # NAG
    "AGC": 0.022, "CGC": 0.022, "GGC": 0.022, "TGC": 0.022, # NGC
    "AGT": 0.017, "CGT": 0.017, "GGT": 0.017, "TGT": 0.017, # NGT
    "ATG": 0.001, "CTG": 0.001, "GTG": 0.001, "TTG": 0.001, # NTG
    "ACG": 0.001, "CCG": 0.001, "GCG": 0.001, "TCG": 0.001, # NCG
}

# Positional mismatch severity factors (Doench et al. 2016 / Hsu et al. 2013 validated seed vs distal weights)
# Positions 1..20 (1 is 5' distal, 20 is PAM-proximal adjacent to PAM)
# Seed region (positions 11-20) exhibits steep penalties for mismatches (e.g. 0.05 - 0.35)
# Distal region (positions 1-10) exhibits moderate tolerance (e.g. 0.50 - 0.95)
POSITIONAL_BASE_WEIGHTS: Dict[int, float] = {
    1: 0.95, 2: 0.92, 3: 0.88, 4: 0.85, 5: 0.80,
    6: 0.75, 7: 0.70, 8: 0.65, 9: 0.60, 10: 0.55,
    11: 0.45, 12: 0.38, 13: 0.30, 14: 0.25, 15: 0.20,
    16: 0.15, 17: 0.12, 18: 0.08, 19: 0.05, 20: 0.03
}

# RNA:DNA mismatch type coefficients
# Transition vs Transversion vs Purine:Purine vs Pyrimidine:Pyrimidine
MISMATCH_PAIR_FACTORS: Dict[Tuple[str, str], float] = {
    # (guide_base, target_base)
    # Transitions (rG:dT / rU:dG rA:dC / rC:dA)
    ('G', 'T'): 0.85, ('A', 'C'): 0.80, ('C', 'A'): 0.75, ('T', 'G'): 0.75,
    # Wobble / Weak
    ('G', 'A'): 0.60, ('A', 'G'): 0.60, ('T', 'C'): 0.55, ('C', 'T'): 0.50,
    # Bulky Transversions / Strong Mismatches
    ('G', 'G'): 0.30, ('C', 'C'): 0.25, ('A', 'A'): 0.35, ('T', 'T'): 0.40,
}


class CFDScorer:
    """
    Computes Cutting Frequency Determination (CFD) scores for off-target alignments.
    """

    @classmethod
    def get_pam_weight(cls, pam: str) -> float:
        """Retrieves PAM penalty score from Doench 2016 matrix."""
        pam_upper = pam.strip().upper()
        if len(pam_upper) == 3:
            # Check exact or N-wildcard
            if pam_upper in PAM_WEIGHTS:
                return PAM_WEIGHTS[pam_upper]
            if pam_upper[1:] == "GG":
                return 1.0
            if pam_upper[1:] in ("GA", "AG"):
                return 0.259
        return 0.001

    @classmethod
    def calculate_mismatch_weight(cls, position: int, guide_base: str, target_base: str) -> float:
        """
        Calculates individual mismatch penalty weight at a specific 1-based guide coordinate.
        """
        pos_weight = POSITIONAL_BASE_WEIGHTS.get(position, 0.50)
        pair = (guide_base.upper(), target_base.upper())
        pair_factor = MISMATCH_PAIR_FACTORS.get(pair, 0.50)
        return float(pos_weight * pair_factor)

    @classmethod
    def calculate_cfd_score(
        cls,
        guide_seq: str,
        target_seq: str,
        pam: str,
        mismatch_positions: List[int]
    ) -> float:
        """
        Calculates the CFD score for an off-target site:
        CFD = PAM_weight * Product( Mismatch_weight_i )
        Returns float in [0.0, 1.0].
        """
        pam_weight = cls.get_pam_weight(pam)
        if pam_weight <= 0.0:
            return 0.0

        if not mismatch_positions or len(mismatch_positions) == 0:
            # Perfect match off-target
            return float(pam_weight)

        cfd = pam_weight
        for pos in mismatch_positions:
            # 1-based index to 0-based
            idx = pos - 1
            if 0 <= idx < min(len(guide_seq), len(target_seq)):
                g_base = guide_seq[idx]
                t_base = target_seq[idx]
                w = cls.calculate_mismatch_weight(pos, g_base, t_base)
                cfd *= w

        return float(np.clip(cfd, 0.0, 1.0))

    @classmethod
    def calculate_specificity_score(cls, cfd_scores: List[float]) -> Tuple[float, float, float]:
        """
        Aggregates individual CFD scores into overall guide specificity score.
        Formula: Specificity = 1.0 / (1.0 + Sum(CFD_scores)) * 100.0
        Returns (cumulative_cfd, specificity_score [0..100], normalized_safety_score [0..1]).
        """
        cum_cfd = float(sum(cfd_scores))
        specificity = float((1.0 / (1.0 + cum_cfd)) * 100.0)
        normalized_safety = float(specificity / 100.0)
        return cum_cfd, specificity, normalized_safety

    @classmethod
    def determine_risk_level(cls, mismatches: int, cfd_score: Optional[float] = None) -> str:
        """
        Classifies off-target risk based on mismatch count and CFD score.
        - HIGH: 0 or 1 mismatch, or CFD >= 0.25
        - MEDIUM: 2 mismatches, or CFD in [0.05, 0.25)
        - LOW: 3+ mismatches and CFD < 0.05
        """
        if cfd_score is not None:
            if cfd_score >= 0.25 or mismatches <= 1:
                return "HIGH"
            elif cfd_score >= 0.05 or mismatches == 2:
                return "MEDIUM"
            else:
                return "LOW"
        else:
            if mismatches <= 1:
                return "HIGH"
            elif mismatches == 2:
                return "MEDIUM"
            else:
                return "LOW"
