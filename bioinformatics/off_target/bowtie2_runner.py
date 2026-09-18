"""
Bowtie2 Alignment Runner for CRISPR Guide RNA Off-Target Discovery.
Executes Bowtie2 against the verified GRCh38 genome index.
"""
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


class Bowtie2Runner:
    """
    Manages execution of Bowtie2 aligner for sensitive CRISPR off-target searches.
    """

    DEFAULT_INDEX_PREFIX = "C:/Users/GeneCureAI/data/bowtie2_index/GRCh38"

    def __init__(self, index_prefix: Optional[str] = None):
        self.index_prefix = index_prefix or self.DEFAULT_INDEX_PREFIX
        self.bowtie2_binary = shutil.which("bowtie2") or shutil.which("bowtie2.exe")

    @property
    def is_index_available(self) -> bool:
        """Verifies presence of standard Bowtie2 index files (.1.bt2, .2.bt2, etc.)."""
        prefix = Path(self.index_prefix)
        # Check standard 32-bit and 64-bit (.bt2 and .bt2l)
        patterns = [f"{prefix}.1.bt2", f"{prefix}.1.bt2l"]
        return any(Path(p).exists() for p in patterns)

    @property
    def is_executable_available(self) -> bool:
        """Verifies if bowtie2 executable is present on the host system."""
        return self.bowtie2_binary is not None

    @property
    def is_ready(self) -> bool:
        """Returns True only if both executable and index are verified."""
        return self.is_executable_available and self.is_index_available

    def align_guides(
        self,
        guides: List[str],
        max_mismatches: int = 3,
        max_alignments: int = 50
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Executes Bowtie2 for a list of candidate 20-nt guide sequences.
        Returns raw SAM output text and execution metadata.
        """
        if not self.is_index_available:
            raise FileNotFoundError(f"Bowtie2 GRCh38 index not found at '{self.index_prefix}'")
        if not self.is_executable_available:
            raise RuntimeError("Bowtie2 executable is not installed or not in PATH.")

        t0 = time.time()
        # Create temporary FASTA query file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".fa", delete=False) as f:
            temp_fa = f.name
            for i, g in enumerate(guides):
                f.write(f">guide_{i+1}\n{g}\n")

        try:
            # Bowtie2 command configured for short 20-nt CRISPR reads
            # -N: max mismatches in seed (0 or 1)
            # -L: seed length (15)
            # -k: search for at most k distinct alignments
            # -f: query input is FASTA format
            # -p: threads (auto/parallel)
            cmd = [
                str(self.bowtie2_binary),
                "-x", str(self.index_prefix),
                "-f", temp_fa,
                "-N", "1",
                "-L", "15",
                "-k", str(max_alignments),
                "--quiet",
                "--no-hd" # Exclude SAM header for faster parsing
            ]

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            sam_output = process.stdout
            exec_time = time.time() - t0

            summary = {
                "status": "SUCCESS",
                "execution_time_seconds": round(exec_time, 4),
                "guides_count": len(guides),
                "index_prefix": self.index_prefix,
                "max_alignments_requested": max_alignments
            }
            return sam_output, summary

        finally:
            if os.path.exists(temp_fa):
                try:
                    os.remove(temp_fa)
                except Exception:
                    pass
