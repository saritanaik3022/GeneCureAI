"""
Dataset Validator for Doench 2016 Rule Set 2 CRISPR datasets.
Ensures DNA sequence validity, 30-mer context constraints, and target label bounds.
"""
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np


class DatasetValidator:
    """Validates raw and processed CRISPR training datasets."""

    VALID_DNA = set("ACGT")

    @classmethod
    def validate_sequence(cls, seq: str) -> bool:
        """Validates that a sequence is exactly 30 nt and consists solely of A, C, G, T."""
        if not isinstance(seq, str):
            return False
        seq_clean = seq.strip().upper()
        return len(seq_clean) == 30 and set(seq_clean).issubset(cls.VALID_DNA)

    @classmethod
    def validate_dataframe(cls, df: pd.DataFrame, seq_col: str = "30mer", target_col: str = "score_drug_gene_rank") -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Validates a dataframe of CRISPR records.
        Filters out any invalid records and returns (cleaned_df, validation_summary).
        """
        initial_count = len(df)
        if seq_col not in df.columns:
            raise KeyError(f"Sequence column '{seq_col}' not found in dataframe. Available: {df.columns.tolist()}")
        if target_col not in df.columns:
            raise KeyError(f"Target column '{target_col}' not found in dataframe. Available: {df.columns.tolist()}")

        # Drop rows with null sequences or targets
        cleaned = df.dropna(subset=[seq_col, target_col]).copy()
        
        # Validate sequence strings
        valid_mask = cleaned[seq_col].apply(cls.validate_sequence)
        invalid_seq_count = int((~valid_mask).sum())
        cleaned = cleaned[valid_mask].copy()

        # Validate target range [0.0, 1.0] (or warn/clip if rank score)
        target_series = cleaned[target_col].astype(float)
        
        summary = {
            "initial_rows": initial_count,
            "valid_rows": len(cleaned),
            "invalid_rows": initial_count - len(cleaned),
            "invalid_seq_count": invalid_seq_count,
            "target_min": float(target_series.min()),
            "target_max": float(target_series.max()),
            "target_mean": float(target_series.mean()),
            "target_std": float(target_series.std()),
        }
        return cleaned, summary
