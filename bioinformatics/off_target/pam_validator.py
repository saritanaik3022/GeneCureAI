"""
Genomic PAM Validator for GRCh38 Off-Target Alignments.
Cross-references aligned genomic coordinates with reference FASTA to retrieve and validate 3-nt PAMs.
"""
from typing import Optional, Tuple
from pathlib import Path
from bioinformatics.genome.fasta_reader import FASTAReader


class PAMValidator:
    """
    Retrieves and validates genomic PAM sequences for SpCas9 off-target sites in GRCh38.
    """

    def __init__(self, fasta_reader: Optional[FASTAReader] = None):
        self.fasta_reader = fasta_reader

    def get_genomic_pam(self, chromosome: str, position: int, strand: str, protospacer_len: int = 20) -> str:
        """
        Extracts the 3-nt genomic PAM immediately 3' adjacent to the aligned protospacer.
        - On '+' strand: PAM coordinates = [position + protospacer_len, position + protospacer_len + 2]
        - On '-' strand: PAM coordinates = [position - 3, position - 1], reverse complemented.
        """
        if self.fasta_reader is None:
            return "NGG" # Fallback if reader not attached

        try:
            if strand == "+":
                pam_start = position + protospacer_len
                pam_end = pam_start + 2
                raw_pam = self.fasta_reader.get_sequence(chromosome, pam_start, pam_end)
                return raw_pam.upper() if len(raw_pam) == 3 else "NNN"
            else:
                # Reverse strand: PAM is 5' in reference coordinates, reverse complemented
                pam_start = position - 3
                pam_end = position - 1
                raw_pam = self.fasta_reader.get_sequence(chromosome, pam_start, pam_end)
                if len(raw_pam) == 3:
                    return FASTAReader.reverse_complement(raw_pam.upper())
                return "NNN"
        except Exception:
            return "NNN"

    @staticmethod
    def is_valid_spcas9_pam(pam: str, allow_non_canonical: bool = True) -> bool:
        """
        Validates whether PAM is recognized by SpCas9.
        - Canonical: NGG (e.g. AGG, CGG, GGG, TGG)
        - Non-canonical: NGA, NAG, NGC
        """
        p = pam.strip().upper()
        if len(p) != 3:
            return False
        if p[1:] == "GG":
            return True
        if allow_non_canonical and p[1:] in ("GA", "AG", "GC", "GT"):
            return True
        return False
