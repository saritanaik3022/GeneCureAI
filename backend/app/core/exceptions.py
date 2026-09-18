"""
Custom exception hierarchy for Gene-Cure AI platform.
"""
from typing import Any, Dict, Optional


class GeneCureException(Exception):
    """Base exception for all Gene-Cure AI errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class GenomeNotAvailableException(GeneCureException):
    """Raised when GRCh38 genomic indices or tools are unavailable in REAL_MODE."""
    def __init__(
        self,
        message: str = "GRCh38 reference genome index is not available. Please run scripts/download_grch38_index.py or switch to DEMO_MODE.",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.code = "GENOME_NOT_AVAILABLE"


class GeneNotFoundException(GeneCureException):
    """Raised when a requested gene symbol is not in the curated registry."""
    def __init__(self, symbol: str):
        super().__init__(
            message=f"Gene '{symbol}' not found in curated cancer gene registry.",
            details={"symbol": symbol}
        )
        self.code = "GENE_NOT_FOUND"


class InvalidSequenceException(GeneCureException):
    """Raised when provided DNA/RNA sequence contains invalid characters or length."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.code = "INVALID_SEQUENCE"


class ModelInferenceException(GeneCureException):
    """Raised when ML model weights or inference execution fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.code = "MODEL_INFERENCE_ERROR"


class TOPSISCalculationException(GeneCureException):
    """Raised when TOPSIS decision matrix or weights are malformed."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.code = "TOPSIS_CALCULATION_ERROR"
