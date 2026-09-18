"""
Reproducible Train / Validation / Test Splitting.
Generates fixed splits with seed=42 and writes data/metadata/doench_dataset_manifest.json.
"""
import os
import json
from typing import Tuple, Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


def create_splits(
    df: pd.DataFrame,
    seq_col: str = "30mer",
    target_col: str = "score_drug_gene_rank",
    train_ratio: float = 0.80,
    val_ratio: float = 0.10,
    test_ratio: float = 0.10,
    random_seed: int = 42,
    group_col: str = "Target gene",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Splits the dataframe into train, validation, and test subsets reproducibly.
    """
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Split ratios must sum to 1.0"

    total_rows = len(df)
    
    # Stratified or group-aware index partitioning with fixed random seed
    train_val_df, test_df = train_test_split(
        df,
        test_size=test_ratio,
        random_state=random_seed,
        shuffle=True
    )
    
    relative_val_ratio = val_ratio / (train_ratio + val_ratio)
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=relative_val_ratio,
        random_state=random_seed,
        shuffle=True
    )
    
    manifest = {
        "dataset_name": "Doench 2016 Rule Set 2",
        "total_rows": int(total_rows),
        "random_seed": int(random_seed),
        "split_strategy": "Reproducible Random Split (80/10/10)",
        "train_rows": int(len(train_df)),
        "validation_rows": int(len(val_df)),
        "test_rows": int(len(test_df)),
        "train_ratio": float(train_ratio),
        "validation_ratio": float(val_ratio),
        "test_ratio": float(test_ratio),
        "sequence_column": seq_col,
        "target_column": target_col,
        "target_stats": {
            "train_mean": float(train_df[target_col].mean()),
            "val_mean": float(val_df[target_col].mean()),
            "test_mean": float(test_df[target_col].mean()),
            "train_std": float(train_df[target_col].std()),
            "val_std": float(val_df[target_col].std()),
            "test_std": float(test_df[target_col].std()),
        },
        "gene_representation": {
            "train_genes": sorted(train_df[group_col].unique().tolist()) if group_col in train_df else [],
            "val_genes": sorted(val_df[group_col].unique().tolist()) if group_col in val_df else [],
            "test_genes": sorted(test_df[group_col].unique().tolist()) if group_col in test_df else [],
        }
    }
    
    return train_df, val_df, test_df, manifest


def save_manifest(manifest: Dict[str, Any], filepath: str = "data/metadata/doench_dataset_manifest.json") -> None:
    """Saves dataset split manifest to JSON."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
