"""
Production Genomic Dataset Bootstrap Script.

Automates initial provisioning of GRCh38 reference assembly and GENCODE v46 GTF
annotations onto persistent volume storage (e.g., Railway Volume at /data).

Features:
1. Idempotent: Checks if files already exist and NEVER re-downloads when present.
2. Direct official mirrors: GENCODE v46 GTF and GRCh38 primary assembly FASTA from EBI.
3. Streamed chunked download & decompression to minimize memory footprint.
4. Automatic .fai indexing via pyfaidx.
5. Local development safe: Bypasses execution when datasets exist locally or when SKIP_BOOTSTRAP is set.
"""
import os
import sys
import gzip
import shutil
import urllib.request
from pathlib import Path
from typing import Optional

# Official dataset URLs (GENCODE Release 46 / GRCh38)
GENCODE_V46_GTF_URL = (
    "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/gencode.v46.annotation.gtf.gz"
)
GRCH38_FASTA_URL = (
    "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/GRCh38.primary_assembly.genome.fa.gz"
)


def log(msg: str):
    """Logs bootstrap progress message."""
    print(f"[BOOTSTRAP] {msg}", flush=True)


def format_bytes(size: int) -> str:
    """Formats bytes to readable units."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024**2:
        return f"{size / 1024:.2f} KB"
    elif size < 1024**3:
        return f"{size / (1024**2):.2f} MB"
    else:
        return f"{size / (1024**3):.2f} GB"


def download_and_extract(url: str, dest_uncompressed_path: Path, label: str):
    """
    Downloads a .gz archive from url and decompresses directly to dest_uncompressed_path.
    Cleans up the intermediate .gz archive upon completion to preserve disk space.
    """
    if dest_uncompressed_path.exists() and dest_uncompressed_path.stat().st_size > 100_000_000:
        log(f"{label} already exists at {dest_uncompressed_path} ({format_bytes(dest_uncompressed_path.stat().st_size)}). Skipping.")
        return

    dest_uncompressed_path.parent.mkdir(parents=True, exist_ok=True)
    temp_gz_path = dest_uncompressed_path.with_name(f"{dest_uncompressed_path.name}.gz.tmp")
    final_gz_path = dest_uncompressed_path.with_name(f"{dest_uncompressed_path.name}.gz")
    temp_dest_path = dest_uncompressed_path.with_name(f"{dest_uncompressed_path.name}.tmp")

    log(f"Starting download for {label} from {url}...")
    headers = {"User-Agent": "GeneCureAI-Production-Bootstrap/1.0"}
    req = urllib.request.Request(url, headers=headers)

    # Download .gz
    with urllib.request.urlopen(req) as resp, open(temp_gz_path, "wb") as out_f:
        total_size = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 8 * 1024 * 1024  # 8 MB chunks
        last_log_mb = 0

        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out_f.write(chunk)
            downloaded += len(chunk)
            curr_mb = downloaded // (50 * 1024 * 1024)
            if curr_mb > last_log_mb:
                last_log_mb = curr_mb
                pct = f"({(downloaded / total_size * 100):.1f}%)" if total_size > 0 else ""
                log(f"Downloaded {format_bytes(downloaded)} / {format_bytes(total_size)} {pct} for {label}")

    if temp_gz_path.exists():
        temp_gz_path.rename(final_gz_path)

    log(f"Download complete: {format_bytes(final_gz_path.stat().st_size)}. Decompressing to {dest_uncompressed_path.name}...")

    # Decompress .gz to final uncompressed file
    with gzip.open(final_gz_path, "rb") as gz_in, open(temp_dest_path, "wb") as f_out:
        shutil.copyfileobj(gz_in, f_out, length=8 * 1024 * 1024)

    # Atomically rename
    temp_dest_path.rename(dest_uncompressed_path)

    # Remove .gz to save disk space
    if final_gz_path.exists():
        final_gz_path.unlink()

    log(f"{label} ready at {dest_uncompressed_path} ({format_bytes(dest_uncompressed_path.stat().st_size)})")


def ensure_fasta_index(fasta_path: Path):
    """Generates .fai index for FASTA if missing using pyfaidx."""
    fai_path = Path(f"{fasta_path}.fai")
    if fai_path.exists() and fai_path.stat().st_size > 0:
        log(f"FASTA index already exists at {fai_path} ({format_bytes(fai_path.stat().st_size)}).")
        return

    log(f"Generating FASTA index for {fasta_path.name} using pyfaidx...")
    try:
        import pyfaidx
        # Initializing pyfaidx.Fasta automatically builds the .fai index on disk
        pyfaidx.Fasta(str(fasta_path), as_raw=True, sequence_always_upper=True)
        log(f"FASTA index created successfully: {fai_path} ({format_bytes(fai_path.stat().st_size)}).")
    except Exception as e:
        log(f"Warning: Could not build pyfaidx index: {e}")


def bootstrap_datasets(
    data_root: Optional[Path] = None,
    genome_fasta: Optional[Path] = None,
    gencode_gtf: Optional[Path] = None
) -> bool:
    """
    Main entry point for verifying and provisioning production datasets.
    Returns True if datasets are ready, False otherwise.
    """
    # Check bypass flags
    if os.getenv("SKIP_BOOTSTRAP", "").lower() in ("1", "true", "yes"):
        log("SKIP_BOOTSTRAP environment variable is set. Skipping bootstrap.")
        return True

    # Resolve target paths
    root = data_root or Path(os.getenv("DATA_ROOT", "/data" if os.name != "nt" else "C:/Users/GeneCureAI/data"))
    fasta_target = genome_fasta or Path(
        os.getenv("GENOME_FASTA", str(root / "genome" / "GRCh38.primary_assembly.genome.fa"))
    )
    gtf_target = gencode_gtf or Path(
        os.getenv("GENCODE_GTF", str(root / "annotation" / "gencode.v46.annotation.gtf"))
    )

    log(f"Checking genomic datasets...")
    log(f"  Target FASTA: {fasta_target} (exists: {fasta_target.exists()})")
    log(f"  Target GTF:   {gtf_target} (exists: {gtf_target.exists()})")

    # Fast check: If both exist and are non-empty, ensure index and exit immediately
    if fasta_target.exists() and fasta_target.stat().st_size > 100_000_000 and gtf_target.exists() and gtf_target.stat().st_size > 100_000_000:
        log("All required genomic datasets already exist and are verified.")
        ensure_fasta_index(fasta_target)
        return True

    # If running locally on Windows and files are missing, do not attempt to write to /data
    if os.name == "nt" and not fasta_target.exists() and not str(fasta_target).startswith("C:"):
        log("Detected Windows environment with unmounted container path. Skipping container bootstrap.")
        return False

    try:
        # Download and decompress GENCODE v46 GTF if missing
        if not (gtf_target.exists() and gtf_target.stat().st_size > 100_000_000):
            download_and_extract(
                url=GENCODE_V46_GTF_URL,
                dest_uncompressed_path=gtf_target,
                label="GENCODE v46 Annotation GTF"
            )

        # Download and decompress GRCh38 FASTA if missing
        if not (fasta_target.exists() and fasta_target.stat().st_size > 100_000_000):
            download_and_extract(
                url=GRCH38_FASTA_URL,
                dest_uncompressed_path=fasta_target,
                label="GRCh38 Primary Assembly FASTA"
            )

        # Build FASTA index
        if fasta_target.exists():
            ensure_fasta_index(fasta_target)

        log("Genomic dataset bootstrap completed successfully.")
        return True

    except Exception as e:
        log(f"ERROR: Dataset bootstrap failed: {e}")
        return False


if __name__ == "__main__":
    success = bootstrap_datasets()
    # In production container startup, exit code 0 allows app to start;
    # if bootstrap fails, exit 1 prevents serving un-provisioned REAL_MODE pipeline
    sys.exit(0 if success else 1)
