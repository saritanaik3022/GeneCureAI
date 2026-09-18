"""
Biophysical and Structural Sequence Filters for Candidate Guide RNAs.
"""
from typing import Tuple, List


class GuideSequenceFilters:
    """
    Computes biophysical properties and evaluates candidate guide suitability.
    """

    COMPLEMENT_MAP = str.maketrans("ACGT", "TGCA")

    @staticmethod
    def calculate_gc_percentage(sequence: str) -> float:
        """
        Calculates GC percentage of a nucleotide sequence:
        GC% = (G + C) / sequence_length * 100
        """
        if not sequence:
            return 0.0
        seq_upper = sequence.upper()
        gc_count = seq_upper.count("G") + seq_upper.count("C")
        return round((gc_count / len(seq_upper)) * 100.0, 2)

    @staticmethod
    def has_poly_t_terminator(sequence: str, threshold: int = 4) -> bool:
        """
        Checks for Pol-III RNA Polymerase termination signal (e.g. TTTT or TTTTT).
        """
        poly_t = "T" * threshold
        return poly_t in sequence.upper()

    @classmethod
    def calculate_self_complementarity(cls, sequence: str, min_stem: int = 4) -> float:
        """
        Estimates self-complementarity / hairpin formation potential
        by scanning for reverse-complement matches within the guide.
        Returns a score normalized between 0.0 and 1.0.
        """
        seq = sequence.upper()
        n = len(seq)
        if n < min_stem * 2:
            return 0.0

        max_matches = 0
        total_possible = (n - min_stem + 1)

        for i in range(n - min_stem + 1):
            kmer = seq[i : i + min_stem]
            kmer_rc = kmer.translate(cls.COMPLEMENT_MAP)[::-1]
            # Check if reverse complement occurs elsewhere non-overlapping in the sequence
            rest = seq[:i] + "N" * min_stem + seq[i + min_stem:]
            if kmer_rc in rest:
                max_matches += 1

        score = min(1.0, max_matches / max(1, total_possible * 0.4))
        return round(score, 3)

    @classmethod
    def evaluate_guide(
        cls,
        protospacer: str,
        gc_min: float = 20.0,
        gc_max: float = 80.0,
        exclude_poly_t: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validates guide candidate against basic biophysical thresholds.
        Does not silently discard; returns pass flag and reasons.
        """
        reasons = []
        is_pass = True

        if len(protospacer) != 20:
            is_pass = False
            reasons.append(f"Invalid protospacer length {len(protospacer)} (expected 20 nt).")

        invalid_bases = set(protospacer.upper()) - set("ACGT")
        if invalid_bases:
            is_pass = False
            reasons.append(f"Invalid non-canonical nucleotides: {invalid_bases}")

        gc = cls.calculate_gc_percentage(protospacer)
        if gc < gc_min:
            is_pass = False
            reasons.append(f"Low GC content: {gc}% (< {gc_min}%).")
        elif gc > gc_max:
            is_pass = False
            reasons.append(f"High GC content: {gc}% (> {gc_max}%).")

        if exclude_poly_t and cls.has_poly_t_terminator(protospacer):
            is_pass = False
            reasons.append("Pol-III termination signal (TTTT) detected.")

        return is_pass, reasons
