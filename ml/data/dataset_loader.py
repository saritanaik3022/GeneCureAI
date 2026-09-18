"""
Dataset Loader for Doench 2016 Rule Set 2.
Loads the real training data from C:\\Users\\GeneCureAI\\data\\doench2016\\doench2016_ruleset2_train.csv
"""
import os
from typing import Tuple, Dict, Any, Optional
import pandas as pd
from ml.data.dataset_validator import DatasetValidator

DEFAULT_DOENCH_PATH = r"C:\Users\GeneCureAI\data\doench2016\doench2016_ruleset2_train.csv"


class DoenchDatasetLoader:
    """Loads and validates the real Doench 2016 Rule Set 2 dataset."""

    def __init__(self, filepath: Optional[str] = None):
        self.filepath = filepath or DEFAULT_DOENCH_PATH

    def load(self, seq_col: str = "30mer", target_col: str = "score_drug_gene_rank") -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Loads the CSV, validates records, and returns (validated_df, summary).
        """
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Doench 2016 dataset not found at '{self.filepath}'")

        df = pd.read_csv(self.filepath)
        cleaned_df, summary = DatasetValidator.validate_dataframe(
            df, seq_col=seq_col, target_col=target_col
        )
        summary["source_path"] = self.filepath
        summary["dataset_name"] = "Doench 2016 Rule Set 2"
        return cleaned_df, summary
