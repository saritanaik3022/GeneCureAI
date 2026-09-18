"""
Stage 1: Gene Service for managing cancer gene registries and biological sequences.
"""
from typing import List, Optional, Dict, Any


class GeneService:
    """Service handling gene data resolution and provenance tracking."""

    @staticmethod
    def get_supported_genes() -> List[str]:
        return [
            "BRCA1", "HER2", "TP53", "EGFR", "KRAS",
            "ALK", "CTNNB1", "AXIN1", "TERT"
        ]

    @staticmethod
    def get_supported_cancers() -> List[str]:
        return ["Breast cancer", "Lung cancer", "Liver cancer"]
