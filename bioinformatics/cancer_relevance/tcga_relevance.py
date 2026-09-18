"""
TCGA Cancer Relevance Service.
Loads and maps real TCGA RNA-seq STAR Counts relevance scores across target indications.
"""
import os
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional
from backend.app.core.config import settings


class TCGACancerRelevanceService:
    """
    Manages lookup of verified TCGA cancer relevance scores.
    Handles gene symbol aliases (e.g., HER2 <-> ERBB2) and cancer indication normalization.
    """

    DEFAULT_CSV_PATH = Path("C:/Users/GeneCureAI/results/cancer_relevance_scores.csv")

    # Cancer type normalization map
    CANCER_MAP: Dict[str, str] = {
        "breast": "Breast",
        "breast cancer": "Breast",
        "lung": "Lung",
        "lung cancer": "Lung",
        "liver": "Liver",
        "liver cancer": "Liver",
    }

    # Gene alias normalization map
    GENE_ALIAS_MAP: Dict[str, str] = {
        "HER2": "ERBB2",
        "ERBB2": "ERBB2",
        "BRCA1": "BRCA1",
        "TP53": "TP53",
        "EGFR": "EGFR",
        "KRAS": "KRAS",
        "ALK": "ALK",
        "CTNNB1": "CTNNB1",
        "AXIN1": "AXIN1",
        "TERT": "TERT",
    }

    def __init__(self, csv_path: Optional[Path] = None):
        self.csv_path = csv_path or self.DEFAULT_CSV_PATH
        self._scores_cache: Dict[Tuple[str, str], float] = {}
        self._mean_expr_cache: Dict[Tuple[str, str], float] = {}
        self._is_loaded = False
        self._load_scores()

    def _load_scores(self):
        if not self.csv_path.exists():
            return

        try:
            df = pd.read_csv(self.csv_path)
            for _, row in df.iterrows():
                c_type = str(row["cancer_type"]).strip()
                gene = str(row["gene"]).strip().upper()
                score = float(row["cancer_relevance_score"])
                mean_expr = float(row["mean_expr"])

                # Store primary
                self._scores_cache[(c_type, gene)] = score
                self._mean_expr_cache[(c_type, gene)] = mean_expr

                # Store aliases
                if gene == "ERBB2":
                    self._scores_cache[(c_type, "HER2")] = score
                    self._mean_expr_cache[(c_type, "HER2")] = mean_expr

            self._is_loaded = True
        except Exception:
            self._is_loaded = False

    @property
    def is_available(self) -> bool:
        return self._is_loaded and len(self._scores_cache) > 0

    def normalize_cancer_type(self, cancer_type: str) -> Optional[str]:
        return self.CANCER_MAP.get(cancer_type.strip().lower())

    def normalize_gene_symbol(self, gene_symbol: str) -> str:
        sym = gene_symbol.strip().upper()
        return self.GENE_ALIAS_MAP.get(sym, sym)

    def get_relevance_score(self, cancer_type: str, gene_symbol: str) -> Optional[float]:
        """
        Retrieves the exact TCGA cancer relevance score for a given cancer type and gene.
        Returns float in [0.0, 1.0] if present, or None if data is not available.
        """
        norm_cancer = self.normalize_cancer_type(cancer_type)
        norm_gene = self.normalize_gene_symbol(gene_symbol)

        if not norm_cancer:
            return None

        # Look up normalized gene
        key = (norm_cancer, norm_gene)
        if key in self._scores_cache:
            return self._scores_cache[key]

        # Try original gene name as fallback
        key_orig = (norm_cancer, gene_symbol.strip().upper())
        if key_orig in self._scores_cache:
            return self._scores_cache[key_orig]

        return None

    def get_mean_expression(self, cancer_type: str, gene_symbol: str) -> Optional[float]:
        """Retrieves raw mean STAR counts expression."""
        norm_cancer = self.normalize_cancer_type(cancer_type)
        norm_gene = self.normalize_gene_symbol(gene_symbol)
        if not norm_cancer:
            return None
        return self._mean_expr_cache.get((norm_cancer, norm_gene))


# Singleton instance
tcga_relevance_service = TCGACancerRelevanceService()
