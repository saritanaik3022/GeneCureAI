"""
Application configuration management using Pydantic Settings and pathlib.
"""
from pathlib import Path
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    All filesystem paths use pathlib.Path for cross-platform robustness.
    """
    APP_NAME: str = "Gene-Cure AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "dev_secret_key_change_in_production_1234567890abcdef"

    # Execution Mode: DEMO_MODE or REAL_MODE
    EXECUTION_MODE: str = "REAL_MODE"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./gene_cure_ai.db"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://genecureai.vercel.app"
    ]

    # Target Cancer Types and Supported Genes
    SUPPORTED_CANCERS: List[str] = [
        "Breast cancer",
        "Lung cancer",
        "Liver cancer"
    ]

    INITIAL_GENE_SET: List[str] = [
        "BRCA1",
        "HER2",
        "TP53",
        "EGFR",
        "KRAS",
        "ALK",
        "CTNNB1",
        "AXIN1",
        "TERT"
    ]

    # TOPSIS Criteria Default Weights (Must sum to 1.0)
    WEIGHT_ON_TARGET: float = 0.35
    WEIGHT_OFF_TARGET_SAFETY: float = 0.30
    WEIGHT_CANCER_RELEVANCE: float = 0.20
    WEIGHT_GC_OPTIMALITY: float = 0.15

    # Configurable Real Dataset Paths (Pathlib compatible)
    DATA_ROOT: Path = Path("C:/Users/GeneCureAI/data")
    GENOME_FASTA: Path = Path("C:/Users/GeneCureAI/data/genome/GRCh38.primary_assembly.genome.fa")
    GENCODE_GTF: Path = Path("C:/Users/GeneCureAI/data/annotation/gencode.v46.annotation.gtf")
    BOWTIE2_INDEX: Path = Path("C:/Users/GeneCureAI/data/bowtie2_index/GRCh38")
    DOENCH_DATA: Path = Path("C:/Users/GeneCureAI/data/doench2016/doench2016_ruleset2_train.csv")
    CANCER_RELEVANCE_DATA: Path = Path("C:/Users/GeneCureAI/results/cancer_relevance_scores.csv")

    # Legacy alias strings
    GRCH38_FASTA_PATH: str = "C:/Users/GeneCureAI/data/genome/GRCh38.primary_assembly.genome.fa"
    GRCH38_BOWTIE2_INDEX: str = "C:/Users/GeneCureAI/data/bowtie2_index/GRCh38"
    BLAST_DB_PATH: str = "./data/references/blast_db/GRCh38"

    # ML Model Checkpoints
    CNN_MODEL_WEIGHTS_PATH: str = "./ml/models/cnn_best_weights.pt"
    XGBOOST_MODEL_PATH: str = "./ml/models/xgb_105_model.json"
    ENSEMBLE_MODEL_PATH: str = "./ml/models/ensemble_meta_learner.joblib"

    # Logging
    LOG_LEVEL: str = "INFO"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            v_trimmed = v.strip()
            if v_trimmed.startswith("[") and v_trimmed.endswith("]"):
                import json
                try:
                    return json.loads(v_trimmed)
                except Exception:
                    pass
            return [origin.strip() for origin in v_trimmed.split(",") if origin.strip()]
        return v

    @field_validator("EXECUTION_MODE")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        v_upper = v.upper()
        if v_upper not in ["DEMO_MODE", "REAL_MODE"]:
            raise ValueError(f"Invalid EXECUTION_MODE '{v}'. Must be either 'DEMO_MODE' or 'REAL_MODE'.")
        return v_upper

    @property
    def is_grch38_available(self) -> bool:
        """Verifies if full GRCh38 genome FASTA and Bowtie2 indices exist."""
        fasta_ok = Path(self.GENOME_FASTA).exists()
        bt2_prefix = Path(self.BOWTIE2_INDEX)
        bt2_ok = Path(f"{bt2_prefix}.1.bt2").exists() or Path(f"{bt2_prefix}.1.bt2l").exists()
        return fasta_ok and bt2_ok

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
