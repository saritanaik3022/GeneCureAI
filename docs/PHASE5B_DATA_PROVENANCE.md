# Phase 5B Complete Data Provenance & Traceability Report

**Report Date**: 2026-08-15  
**Project**: Gene-Cure AI  
**Pipeline Version**: 1.0.0 (Phase 5B Real Integrated Engine)

---

## 1. End-to-End Computational Provenance Chain

Every ranked CRISPR candidate guide produced by the Gene-Cure AI platform is fully traceable to authentic open-access biological datasets, trained neural/tree models, aligner indices, and multi-attribute mathematical decision models.

```
GENCODE v46 Annotation (GTF) 
  + GRCh38 Primary Assembly Genome (FASTA)
        │
        ▼
Dual-Strand SpCas9 Exon Scanning (5'-NGG-3' PAM)
        │
        ▼
Candidate 20-nt Protospacers + 30-nt Contexts
        │
        ├─────────────────────────────┬─────────────────────────────┬─────────────────────────────┐
        ▼                             ▼                             ▼                             ▼
On-Target ML Prediction       Off-Target Alignment          TCGA STAR Counts              GC Optimality
(Hybrid 1D-CNN + XGBoost)     (Bowtie2 + CFD Matrix)        (RNA-seq Expression)          (1 - 2|GC - 0.50|)
[w1 = 0.35]                   [w2 = 0.30]                   [w3 = 0.20]                   [w4 = 0.15]
        │                             │                             │                             │
        └─────────────────────────────┴──────────────┬──────────────┴─────────────────────────────┘
                                                     ▼
                                        Decision Matrix X [m × 4]
                                                     │
                                                     ▼
                                       Vector Normalization (r_ij)
                                                     │
                                                     ▼
                                         Weighted Matrix (v_ij)
                                                     │
                                                     ▼
                                      Positive (A+) & Negative (A-) Ideals
                                                     │
                                                     ▼
                                     Euclidean Separation (S_i+, S_i-)
                                                     │
                                                     ▼
                                      Relative Closeness Score (C_i)
                                                     │
                                                     ▼
                                           Final Guide Ranking
```

---

## 2. Component Provenance Specification

| Component | Source / Resource | Path / File Identifier | Exact Version | Provenance Type |
| :--- | :--- | :--- | :--- | :--- |
| **Gene Annotation** | GENCODE Comprehensive | `C:\Users\GeneCureAI\data\annotation\gencode.v46.annotation.gtf` | Release 46 (GRCh38) | SOURCE-DERIVED |
| **Reference Genome** | NCBI / Ensembl GRCh38 | `C:\Users\GeneCureAI\data\genome\GRCh38.primary_assembly.genome.fa` | Primary Assembly | SOURCE-DERIVED |
| **On-Target Training** | Doench et al., *Nat Biotechnol* 2016 | `C:\Users\GeneCureAI\data\doench2016\doench2016_ruleset2_train.csv` | Rule Set 2 (5,310 samples) | SOURCE-DERIVED |
| **Feature Representation**| Gene-Cure AI 105 Features | `ml/features/feature_schema.py` | `gene-cure-v1-105` | ENGINEERED BIOPHYSICAL |
| **On-Target Models** | PyTorch 1D-CNN + XGBoost Ensemble | `ml/models/hybrid/hybrid_model.json` | v1.0.0-Hybrid | COMPUTED MODEL |
| **Off-Target Search** | Bowtie2 Index | `C:\Users\GeneCureAI\data\bowtie2_index\GRCh38.*.bt2` | GRCh38 6-file index | SOURCE-DERIVED |
| **CFD Cleavage Matrix** | Doench et al. (Nat Biotechnol 2016) | `bioinformatics/off_target/cfd_scorer.py` | Official 2016 Matrix | SOURCE-DERIVED |
| **Cancer Expression** | TCGA RNA-seq STAR Counts | `C:\Users\GeneCureAI\results\cancer_relevance_scores.csv` | TCGA Cohorts (Breast, Lung, Liver) | SOURCE-DERIVED |
| **GC Optimality** | Gene-Cure AI Model | `backend/app/services/topsis_service.py` | Linear 50% deviation penalty | ENGINEERED METRIC |
| **TOPSIS Engine** | Hwang & Yoon (1981) Math | `ranking/topsis.py` | Standard Vector Norm | MATHEMATICAL MODEL |

---

## 3. Candidate Traceability Fields

Every ranked item returned by `GET /api/v1/ranking/{run_id}` or `POST /api/v1/pipeline/execute` includes complete traceability metadata:
- `guide_id`: Unique identifier (e.g. `guide-brca1-01`)
- `protospacer_sequence`: 20-nt guide sequence (5' $\to$ 3')
- `pam`: 3-nt genomic PAM
- `strand`: Target strand (`+` or `-`)
- `chromosome`: Target chromosome
- `genomic_start`, `genomic_end`: 1-based inclusive genomic coordinates in GRCh38
- `context_30nt`: 30-nt genomic sequence context
- `on_target_criterion`, `off_target_criterion`, `cancer_relevance_criterion`, `gc_optimality_criterion`: The 4 raw criteria values
- `closeness_score`: TOPSIS relative closeness score $C_i \in [0, 1]$
- `rank`: Integer rank ($1, 2, 3, \dots$)
- `ranking_status`: `RANKED` or `INCOMPLETE`
