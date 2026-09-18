"""
GRCh38 Reference Genome FASTA Reader with Random-Access Indexing (pyfaidx / samtools FAI).
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import os

try:
    import pyfaidx
    PYFAIDX_AVAILABLE = True
except ImportError:
    PYFAIDX_AVAILABLE = False


class FASTAReader:
    """
    Random-access reader for large reference genome FASTA files.
    Prefers pyfaidx for fast indexed querying, with built-in samtools FAI byte seeking fallback.
    """

    COMPLEMENT_MAP = str.maketrans("ACGTNacgtn", "TGCANtgcan")

    def __init__(self, fasta_path: Path):
        self.fasta_path = Path(fasta_path)
        self.fai_path = Path(f"{fasta_path}.fai")
        self._pyfaidx_fasta: Optional[object] = None
        self._fai_index: Dict[str, Tuple[int, int, int, int]] = {} # name -> (length, offset, line_blen, file_blen)
        self._contig_name_map: Dict[str, str] = {} # normalized -> actual contig in FASTA
        self._init_reader()

    def _init_reader(self):
        if not self.fasta_path.exists():
            raise FileNotFoundError(f"Reference genome FASTA not found at: {self.fasta_path}")

        if PYFAIDX_AVAILABLE:
            try:
                self._pyfaidx_fasta = pyfaidx.Fasta(str(self.fasta_path), as_raw=True, sequence_always_upper=True)
                for key in self._pyfaidx_fasta.keys():
                    self._map_contig_name(key)
                return
            except Exception:
                self._pyfaidx_fasta = None

        # Fallback to direct FAI index reading
        self._load_fai()

    def _map_contig_name(self, actual_name: str):
        self._contig_name_map[actual_name] = actual_name
        self._contig_name_map[actual_name.lower()] = actual_name
        if actual_name.startswith("chr"):
            no_chr = actual_name[3:]
            self._contig_name_map[no_chr] = actual_name
            self._contig_name_map[no_chr.lower()] = actual_name
        else:
            with_chr = f"chr{actual_name}"
            self._contig_name_map[with_chr] = actual_name
            self._contig_name_map[with_chr.lower()] = actual_name

    def _load_fai(self):
        if not self.fai_path.exists():
            raise FileNotFoundError(
                f"FASTA index (.fai) not found at: {self.fai_path}. "
                "Indexed access requires a valid .fai index file."
            )
        with open(self.fai_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 5:
                    name, length, offset, line_blen, file_blen = (
                        parts[0], int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
                    )
                    self._fai_index[name] = (length, offset, line_blen, file_blen)
                    self._map_contig_name(name)

    def resolve_chromosome(self, chrom: str) -> str:
        """Resolves chromosome naming discrepancies (e.g. '17' vs 'chr17')."""
        if chrom in self._contig_name_map:
            return self._contig_name_map[chrom]
        chrom_clean = chrom.strip()
        if chrom_clean in self._contig_name_map:
            return self._contig_name_map[chrom_clean]
        raise KeyError(f"Chromosome '{chrom}' not found in FASTA index.")

    @classmethod
    def reverse_complement(cls, sequence: str) -> str:
        """Computes the reverse complement of a DNA nucleotide string."""
        return sequence.translate(cls.COMPLEMENT_MAP)[::-1]

    def get_sequence(self, chrom: str, start: int, end: int) -> str:
        """
        Extracts 1-based inclusive genomic interval [start, end] from FASTA file.
        Returns uppercase DNA nucleotide string (5' -> 3' along the positive strand).
        """
        actual_chrom = self.resolve_chromosome(chrom)

        if start < 1:
            start = 1

        if self._pyfaidx_fasta is not None:
            # pyfaidx uses 0-based start, 1-based end in slicing or 1-based with object notation
            # [start-1:end] gives [start, end] inclusive in 1-based
            record = self._pyfaidx_fasta[actual_chrom]
            chrom_len = len(record)
            if end > chrom_len:
                end = chrom_len
            if start > end:
                return ""
            seq = record[start - 1 : end]
            return str(seq).upper()

        # Fallback via direct seek in FAI
        length, offset, line_blen, file_blen = self._fai_index[actual_chrom]
        if end > length:
            end = length
        if start > end:
            return ""

        req_length = end - start + 1
        zero_start = start - 1
        newlines_before = zero_start // line_blen
        byte_start = offset + zero_start + newlines_before * (file_blen - line_blen)

        newlines_in_region = (zero_start + req_length) // line_blen - zero_start // line_blen
        bytes_to_read = req_length + newlines_in_region * (file_blen - line_blen) + 128

        with open(self.fasta_path, "rb") as f:
            f.seek(byte_start)
            raw_bytes = f.read(bytes_to_read)

        seq_text = raw_bytes.decode("ascii", errors="ignore").replace("\n", "").replace("\r", "")
        return seq_text[:req_length].upper()

    def get_contig_length(self, chrom: str) -> int:
        """Returns the total sequence length of a chromosome/contig."""
        actual_chrom = self.resolve_chromosome(chrom)
        if self._pyfaidx_fasta is not None:
            return len(self._pyfaidx_fasta[actual_chrom])
        return self._fai_index[actual_chrom][0]
