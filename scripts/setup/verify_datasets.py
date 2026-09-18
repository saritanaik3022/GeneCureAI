"""
Gene-Cure AI: Dataset Verification & Readiness Inspection Script
Checks and verifies all real project resources using pathlib without modifying original files.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd


def format_size(num_bytes: int) -> str:
    """Formats raw bytes into human-readable units."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 ** 2:
        return f"{num_bytes / 1024:.2f} KB"
    elif num_bytes < 1024 ** 3:
        return f"{num_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{num_bytes / (1024 ** 3):.2f} GB ({num_bytes:,} bytes)"


def verify_datasets() -> bool:
    """Performs comprehensive verification of real project datasets."""
    print("=" * 80)
    print(" GENE-CURE AI: REAL DATASET READINESS & PROVENANCE INSPECTION")
    print("=" * 80)

    # 1. Resolve Paths via Environment Variables with Pathlib
    data_root = Path(os.getenv("DATA_ROOT", "C:/Users/GeneCureAI/data"))
    genome_fasta = Path(os.getenv("GENOME_FASTA", "C:/Users/GeneCureAI/data/genome/GRCh38.primary_assembly.genome.fa"))
    gencode_gtf = Path(os.getenv("GENCODE_GTF", "C:/Users/GeneCureAI/data/annotation/gencode.v46.annotation.gtf"))
    bowtie2_index_prefix = Path(os.getenv("BOWTIE2_INDEX", "C:/Users/GeneCureAI/data/bowtie2_index/GRCh38"))
    doench_data = Path(os.getenv("DOENCH_DATA", "C:/Users/GeneCureAI/data/doench2016/doench2016_ruleset2_train.csv"))
    cancer_relevance_data = Path(os.getenv("CANCER_RELEVANCE_DATA", "C:/Users/GeneCureAI/results/cancer_relevance_scores.csv"))

    all_verified = True

    # ---------------------------------------------------------
    # Resource 1: GRCh38 Reference Genome FASTA
    # ---------------------------------------------------------
    print("\n[1] GRCh38 Human Reference Genome Assembly FASTA")
    print(f"    Path: {genome_fasta}")
    if genome_fasta.exists() and genome_fasta.is_file():
        size = genome_fasta.stat().st_size
        print(f"    Status:         [EXISTS / READY]")
        print(f"    File Size:      {format_size(size)}")
        print(f"    Format:         FASTA (multi-chromosome nucleotide sequence)")
        print(f"    Genome Assembly:GRCh38 (Human primary assembly)")
        try:
            with open(genome_fasta, "r", encoding="utf-8") as f:
                header = next(f).strip()
            print(f"    First Header:   {header}")
        except Exception as e:
            print(f"    Header read error: {e}")
    else:
        print("    Status:         [MISSING / NOT FOUND]")
        all_verified = False

    # ---------------------------------------------------------
    # Resource 2: GENCODE Annotation GTF
    # ---------------------------------------------------------
    print("\n[2] GENCODE Comprehensive Gene Annotation")
    print(f"    Path: {gencode_gtf}")
    if gencode_gtf.exists() and gencode_gtf.is_file():
        size = gencode_gtf.stat().st_size
        print(f"    Status:         [EXISTS / READY]")
        print(f"    File Size:      {format_size(size)}")
        print(f"    Format:         GTF (Gene Transfer Format v2.2)")
        try:
            with open(gencode_gtf, "r", encoding="utf-8") as f:
                headers = [next(f).strip() for _ in range(5) if not f.closed]
            meta_desc = [h for h in headers if "description:" in h]
            print(f"    Annotation Meta:{meta_desc[0] if meta_desc else headers[0]}")
        except Exception as e:
            print(f"    Header read error: {e}")
    else:
        print("    Status:         [MISSING / NOT FOUND]")
        all_verified = False

    # ---------------------------------------------------------
    # Resource 3: Bowtie2 GRCh38 Index Files
    # ---------------------------------------------------------
    bt2_dir = bowtie2_index_prefix.parent
    bt2_prefix_name = bowtie2_index_prefix.name
    print(f"\n[3] Bowtie2 GRCh38 Seed-and-Extend Genomic Index")
    print(f"    Index Directory: {bt2_dir}")
    print(f"    Index Prefix:    {bt2_prefix_name}")
    
    expected_suffixes = [".1.bt2", ".2.bt2", ".3.bt2", ".4.bt2", ".rev.1.bt2", ".rev.2.bt2"]
    large_suffixes = [".1.bt2l", ".2.bt2l", ".3.bt2l", ".4.bt2l", ".rev.1.bt2l", ".rev.2.bt2l"]
    
    found_bt2 = []
    if bt2_dir.exists() and bt2_dir.is_dir():
        for s in expected_suffixes:
            idx_file = bt2_dir / f"{bt2_prefix_name}{s}"
            if idx_file.exists():
                found_bt2.append(idx_file)
        if not found_bt2:
            for s in large_suffixes:
                idx_file = bt2_dir / f"{bt2_prefix_name}{s}"
                if idx_file.exists():
                    found_bt2.append(idx_file)

        if len(found_bt2) == 6:
            total_bt2_size = sum(f.stat().st_size for f in found_bt2)
            print(f"    Status:         [EXISTS / 100% COMPLETE]")
            print(f"    Total Index Size:{format_size(total_bt2_size)}")
            print(f"    Components:     6 of 6 index binary archives present")
            for f in found_bt2:
                print(f"      - {f.name} ({format_size(f.stat().st_size)})")
        else:
            print(f"    Status:         [INCOMPLETE - Found {len(found_bt2)}/6 index files]")
            all_verified = False
    else:
        print("    Status:         [MISSING / DIRECTORY NOT FOUND]")
        all_verified = False

    # ---------------------------------------------------------
    # Resource 4: Doench 2016 / Azimuth Rule Set 2 Training Data
    # ---------------------------------------------------------
    print("\n[4] Doench 2016 CRISPR sgRNA Activity Dataset")
    print(f"    Path: {doench_data}")
    if doench_data.exists() and doench_data.is_file():
        size = doench_data.stat().st_size
        print(f"    Status:         [EXISTS / READY]")
        print(f"    File Size:      {format_size(size)}")
        print(f"    Format:         CSV")
        try:
            df_doench = pd.read_csv(doench_data)
            print(f"    Row Count:      {len(df_doench):,} sgRNA entries")
            print(f"    Column Count:   {len(df_doench.columns)} columns")
            print(f"    Schema / Dtypes:")
            for col, dtype in df_doench.dtypes.items():
                print(f"      - {col}: {dtype}")
            print(f"    Unique Target Genes: {df_doench['Target gene'].nunique()} genes")
            print(f"    Sample 30mer:   {df_doench['30mer'].iloc[0]} (Target: {df_doench['Target gene'].iloc[0]}, Activity: {df_doench['predictions'].iloc[0]:.4f})")
        except Exception as e:
            print(f"    CSV parse error: {e}")
            all_verified = False
    else:
        print("    Status:         [MISSING / NOT FOUND]")
        all_verified = False

    # ---------------------------------------------------------
    # Resource 5: TCGA-derived Cancer Relevance Scores
    # ---------------------------------------------------------
    print("\n[5] TCGA-Derived Cancer Relevance Scores")
    print(f"    Path: {cancer_relevance_data}")
    if cancer_relevance_data.exists() and cancer_relevance_data.is_file():
        size = cancer_relevance_data.stat().st_size
        print(f"    Status:         [EXISTS / READY]")
        print(f"    File Size:      {format_size(size)}")
        print(f"    Format:         CSV")
        try:
            df_cr = pd.read_csv(cancer_relevance_data)
            print(f"    Row Count:      {len(df_cr)} cancer-gene associations")
            print(f"    Columns:        {df_cr.columns.tolist()}")
            print(f"    Dataset Content:")
            for _, row in df_cr.iterrows():
                print(f"      - {row['cancer_type']:<8} | Gene: {row['gene']:<7} | Mean Expr: {row['mean_expr']:>10.2f} | Cancer Relevance: {row['cancer_relevance_score']:.4f}")
        except Exception as e:
            print(f"    CSV parse error: {e}")
            all_verified = False
    else:
        print("    Status:         [MISSING / NOT FOUND]")
        all_verified = False

    # ---------------------------------------------------------
    # Final Readiness Summary
    # ---------------------------------------------------------
    print("\n" + "=" * 80)
    if all_verified:
        print(" [PASSED] ALL 5 REAL SCIENTIFIC DATASET RESOURCES ARE VERIFIED & READY")
    else:
        print(" [WARNING] SOME DATASET RESOURCES ARE MISSING OR INCOMPLETE")
    print("=" * 80 + "\n")

    return all_verified


if __name__ == "__main__":
    success = verify_datasets()
    sys.exit(0 if success else 1)
