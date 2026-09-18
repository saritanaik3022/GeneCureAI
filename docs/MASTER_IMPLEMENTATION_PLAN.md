# Master Implementation Plan: Gene-Cure AI
**A Deep Learning-Driven Platform for Automated CRISPR Guide RNA Design Targeting Breast, Lung, and Liver Cancer Therapeutics**

> **Mandatory Disclaimer**: This platform provides *in-silico* computational predictions and is not a substitute for experimental validation in molecular biology or clinical laboratories. All generated guide RNAs, efficiency predictions, and off-target safety evaluations must undergo wet-lab functional validation before any biological or therapeutic application.

---

## Executive Summary & Engineering Philosophy
Gene-Cure AI integrates computational genomics, deep learning sequence analysis, gradient-boosted decision trees with bio-physicochemical feature engineering, seed-and-extend off-target search, and multi-criteria decision making (TOPSIS) into a cohesive 5-stage automated pipeline.

The platform strictly adheres to rigorous scientific and software standards:
1. **Scientific Integrity**: No synthetic or fabricated model performance, gene sequences, or experimental metrics.
2. **Deterministic Dual-Mode Operation**: Seamless transition between **REAL MODE** (requiring local GRCh38 indices, BLAST+/Bowtie2, and trained PyTorch/XGBoost weights) and **DEMO MODE** (deterministic, pre-computed reference fixtures for instant offline evaluation without missing data fallbacks).
3. **Data Provenance**: Every biological record (NCBI Gene IDs, Ensembl Transcript IDs, HGNC symbols, PubMed references, PAM coordinates) maintains end-to-end provenance traceable to authoritative genomic databases.
4. **Computational Efficiency**: Hybrid CPU/GPU ML inference, vectorized sequence operations with Biopython, and optimized multi-attribute ranking.

---

## A. System Architecture

```
                                  +-------------------------------------------------------------+
                                  |                     USER / RESEARCHER                      |
                                  +------------------------------+------------------------------+
                                                                 |
                                                                 v
+-------------------------------------------------------------------------------------------------------------------------------+
|                                                PRESENTATION LAYER (Frontend)                                                 |
|  React 18 + TypeScript + Vite + TailwindCSS + Lucide Icons + Recharts                                                         |
|  - Cancer & Gene Catalog Browser         - Interactive Guide RNA Studio & Genome Visualizer                                    |
|  - On-Target ML Explanation Dashboard   - Off-Target Heatmap & CFD Mismatch Inspector                                         |
|  - TOPSIS Sensitivity & Ranking Studio   - Provenance & Audit Trail Export (FASTA / GenBank / CSV / PDF)                       |
+----------------------------------------------------------------+--------------------------------------------------------------+
                                                                 | HTTPS / REST API / SSE
                                                                 v
+-------------------------------------------------------------------------------------------------------------------------------+
|                                                 APPLICATION LAYER (FastAPI Backend)                                           |
|  FastAPI (Python 3.10) + Pydantic v2 + SQLAlchemy 2.0 (Async) + Celery / BackgroundTasks                                     |
|  +-------------------------------------------------------------------------------------------------------------------------+  |
|  |  Pipeline Orchestrator & Mode Manager (REAL_MODE vs. DEMO_MODE)                                                         |  |
|  +-------------------------------------------------------------------------------------------------------------------------+  |
|  | Stage 1: Gene Registry & NCBI/Ensembl Ingestion Service                                                                |  |
|  | Stage 2: SpCas9 Guide Scanner (20nt + NGG, Forward & Reverse Complement, GC Filtering)                                  |  |
|  | Stage 3: Hybrid On-Target ML Service (PyTorch 1D-CNN + XGBoost 105-Feature Vectorizer + Stacking Regressor)             |  |
|  | Stage 4: Off-Target Engine (Bowtie2 Seed-and-Extend / BLAST+ Local Search / CFD Matrix Scorer / Fallback Manager)        |  |
|  | Stage 5: Multi-Criteria Ranking Engine (TOPSIS Vector Normalization + Dynamic Weighting + Closeness Scoring)             |  |
|  +-------------------------------------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------------+--------------------------------------------------------------+
                                                                 |
               +-------------------------------------------------+-------------------------------------------------+
               |                                                                                                   |
               v                                                                                                   v
+-------------------------------------------------------+                 +-------------------------------------------------------+
|                STORAGE & COMPUTE LAYER                |                 |               GENOMIC & ML ARTIFACTS                  |
|  - PostgreSQL 15+ (Relational metadata, guides,       |                 |  - Model Weights: cnn_v1.pt, xgb_105_v1.json          |
|    evaluations, runs, user audit logs)                |                 |  - Training Data: Doench 2016 Rule Set 2 (HCT116,    |
|  - Redis 7 (Caching, async job state, rate-limiting)  |                 |    293T, EL4, AML screen datasets)                    |
|  - Local File System / S3: BLAST databases, Bowtie2   |                 |  - GRCh38 Genomic Indices (External download script)  |
|    indexes, pre-computed demo fixtures                |                 |  - CFD Scoring Matrices (Doench 2016 mismatch costs)  |
+-------------------------------------------------------+                 +-------------------------------------------------------+
```

---

## B. Complete Folder Structure

```
GeneCureAI/
├── .github/
│   └── workflows/
│       ├── backend-ci.yml
│       ├── frontend-ci.yml
│       └── docker-build.yml
├── docs/
│   ├── MASTER_IMPLEMENTATION_PLAN.md
│   ├── API_SPECIFICATION.md
│   ├── ML_METHODOLOGY.md
│   ├── FEATURE_ENGINEERING_105.md
│   ├── GENOME_SETUP_GUIDE.md
│   └── PROVENANCE_DATA_DICTIONARY.md
├── scripts/
│   ├── setup_environment.sh
│   ├── setup_environment.bat
│   ├── download_grch38_index.py
│   ├── download_doench2016_dataset.py
│   ├── precompute_demo_fixtures.py
│   └── train_models.py
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── database.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── health.py
│   │   │   │   │   ├── cancer_genes.py
│   │   │   │   │   ├── guide_design.py
│   │   │   │   │   ├── on_target_prediction.py
│   │   │   │   │   ├── off_target_analysis.py
│   │   │   │   │   ├── topsis_ranking.py
│   │   │   │   │   ├── pipeline_execution.py
│   │   │   │   │   └── export.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── cancer_gene.py
│   │   │   ├── guide_rna.py
│   │   │   ├── on_target.py
│   │   │   ├── off_target.py
│   │   │   ├── topsis.py
│   │   │   ├── pipeline.py
│   │   │   └── provenance.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── cancer_gene.py
│   │   │   ├── guide_rna.py
│   │   │   ├── on_target_score.py
│   │   │   ├── off_target_site.py
│   │   │   ├── topsis_result.py
│   │   │   └── pipeline_run.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── gene_service.py
│   │   │   ├── guide_scanner_service.py
│   │   │   ├── on_target_ml_service.py
│   │   │   ├── feature_extractor_105.py
│   │   │   ├── off_target_service.py
│   │   │   ├── cfd_scorer.py
│   │   │   ├── topsis_service.py
│   │   │   └── pipeline_orchestrator.py
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   ├── cnn_model.py
│   │   │   ├── xgboost_model.py
│   │   │   ├── ensemble_stacker.py
│   │   │   ├── feature_builder.py
│   │   │   ├── dataset_loader.py
│   │   │   ├── evaluation_metrics.py
│   │   │   └── weights/
│   │   │       ├── .gitkeep
│   │   │       ├── cnn_best_weights.pt
│   │   │       ├── xgb_105_model.json
│   │   │       └── ensemble_meta_learner.joblib
│   │   ├── bioinformatics/
│   │   │   ├── __init__.py
│   │   │   ├── blast_wrapper.py
│   │   │   ├── bowtie2_wrapper.py
│   │   │   ├── cfd_matrix_loader.py
│   │   │   ├── vienna_rna_wrapper.py
│   │   │   └── sequence_utils.py
│   │   ├── fixtures/
│   │   │   ├── demo_genes.json
│   │   │   ├── demo_guides.json
│   │   │   ├── demo_off_targets.json
│   │   │   ├── demo_topsis_rankings.json
│   │   │   └── cfd_matrices/
│   │   │       ├── mismatch_score.pkl
│   │   │       └── pam_scores.pkl
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       └── mode_checker.py
│   └── tests/
│       ├── conftest.py
│       ├── test_gene_service.py
│       ├── test_guide_scanner.py
│       ├── test_feature_extractor_105.py
│       ├── test_on_target_ml.py
│       ├── test_off_target_engine.py
│       ├── test_topsis_ranking.py
│       └── test_full_pipeline_e2e.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── routes/
│   │   │   └── AppRouter.tsx
│   │   ├── types/
│   │   │   ├── cancer_gene.types.ts
│   │   │   ├── guide_rna.types.ts
│   │   │   ├── on_target.types.ts
│   │   │   ├── off_target.types.ts
│   │   │   ├── topsis.types.ts
│   │   │   ├── pipeline.types.ts
│   │   │   └── api.types.ts
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── cancerGeneApi.ts
│   │   │   ├── guideDesignApi.ts
│   │   │   ├── onTargetApi.ts
│   │   │   ├── offTargetApi.ts
│   │   │   ├── topsisApi.ts
│   │   │   └── pipelineApi.ts
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Navbar.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   ├── ModeBadge.tsx
│   │   │   │   ├── ScientificDisclaimerModal.tsx
│   │   │   │   ├── MetricCard.tsx
│   │   │   │   ├── LoadingSpinner.tsx
│   │   │   │   └── ProvenanceBadge.tsx
│   │   │   ├── gene_selection/
│   │   │   │   ├── CancerTypeSelector.tsx
│   │   │   │   ├── GeneCard.tsx
│   │   │   │   ├── GeneDetailDrawer.tsx
│   │   │   │   └── GeneProvenanceViewer.tsx
│   │   │   ├── guide_design/
│   │   │   │   ├── SequenceInputForm.tsx
│   │   │   │   ├── GuideCandidateTable.tsx
│   │   │   │   ├── GCContentDistributionChart.tsx
│   │   │   │   └── ExonIntronMapViewer.tsx
│   │   │   ├── on_target/
│   │   │   │   ├── HybridScoreSummary.tsx
│   │   │   │   ├── CNNFeatureMapVisualizer.tsx
│   │   │   │   ├── XGBoostFeatureImportancePlot.tsx
│   │   │   │   └── PositionWeightLogo.tsx
│   │   │   ├── off_target/
│   │   │   │   ├── OffTargetSummaryMetrics.tsx
│   │   │   │   ├── GenomicMismatchAligner.tsx
│   │   │   │   ├── CFDScoreDistribution.tsx
│   │   │   │   └── GenomeMissingWarning.tsx
│   │   │   ├── topsis/
│   │   │   │   ├── WeightCustomizerSlider.tsx
│   │   │   │   ├── DecisionMatrixTable.tsx
│   │   │   │   ├── IdealDistanceRadarChart.tsx
│   │   │   │   └── RankedGuideList.tsx
│   │   │   └── export/
│   │   │       ├── ExportReportDialog.tsx
│   │   │       └── FastaGenBankDownloader.tsx
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   ├── GeneCatalogPage.tsx
│   │   │   ├── GuideDesignStudioPage.tsx
│   │   │   ├── OnTargetEvaluationPage.tsx
│   │   │   ├── OffTargetSafetyPage.tsx
│   │   │   ├── TOPSISRankingPage.tsx
│   │   │   ├── PipelineWizardPage.tsx
│   │   │   ├── ModelValidationReportPage.tsx
│   │   │   └── SystemStatusPage.tsx
│   │   ├── hooks/
│   │   │   ├── useSystemMode.ts
│   │   │   ├── usePipelineRunner.ts
│   │   │   └── useGeneData.ts
│   │   └── utils/
│   │       ├── formatting.ts
│   │       ├── sequenceColors.ts
│   │       └── exportHelpers.ts
│   └── tests/
│       ├── App.test.tsx
│       ├── GuideCandidateTable.test.tsx
│       └── TOPSISCustomizer.test.tsx
├── data/
│   ├── README.md
│   ├── doench2016/
│   │   └── .gitkeep
│   ├── references/
│   │   ├── .gitkeep
│   │   └── demo_transcripts.fasta
│   └── cfd_matrices/
│       └── cfd_matrices.json
├── docker-compose.yml
├── docker-compose.prod.yml
├── .gitignore
├── .dockerignore
└── README.md
```

---

## C. End-to-End Data Flow

```
[Cancer / Target Gene Selection: BRCA1, EGFR, TP53, etc.]
                      │
                      ▼
[Stage 1: Gene Resolution & CDS Sequence Extraction]
   • Fetch Canonical Transcript (e.g., ENST00000357654 for BRCA1)
   • Extract Exonic Coding Sequence (CDS) + Flanking Context
   • Record Provenance: HGNC ID, NCBI Gene ID, Assembly GRCh38.p14
                      │
                      ▼
[Stage 2: SpCas9 In-Silico Guide RNA Scanning]
   • Scan 5' -> 3' Forward Strand & Reverse Complement for PAM (5'-NGG-3')
   • Extract 20-nt Protospacer (Positions -20 to -1 relative to PAM)
   • Extract Extended Context: 30-nt window (4nt 5' + 20nt Guide + 3nt PAM + 3nt 3')
   • Compute Basic Metrics: GC%, Poly-T stretches (terminators), Self-complementarity
                      │
                      ▼
[Stage 3: Hybrid On-Target Efficiency Prediction (CNN + XGBoost)]
   ├──> Branch A (CNN): 30-nt One-Hot Encoded Matrix (4 x 30) -> Conv1D -> BatchNorm -> MaxPool -> Dense
   └──> Branch B (XGBoost): 105 Engineered Bio-physicochemical Features (Positional 1-mer/2-mer, GC%, Thermodynamics)
                      │
                      ▼
        [Meta-Stacking Model / Blended Ensemble Output]
        On-Target Efficiency Score: E ∈ [0.0, 1.0] (Calibrated Percentile / Efficacy)
                      │
                      ▼
[Stage 4: Seed-and-Extend Off-Target Analysis]
   • Check Environment: REAL MODE (GRCh38 Bowtie2/BLAST+) vs. DEMO MODE (Stored Fixtures)
   • If REAL MODE and GRCh38 Missing: Flag `GENOME_NOT_AVAILABLE` & Halt Stage 4
   • Execute Seed Alignment (PAM-proximal 12-nt seed, up to 3 mismatches in seed, 6 total)
   • Compute CFD (Cutting Frequency Determination) Score per Off-Target Hit
   • Calculate Cumulative Specificity Score:
     S_spec = 100 / (100 + Σ CFD_i)   =>   Normalized Off-Target Safety Score: O ∈ [0.0, 1.0]
                      │
                      ▼
[Stage 5: TOPSIS Multi-Criteria Decision Ranking]
   • Construct Decision Matrix (m candidate guides × 4 criteria):
     C1: On-Target Efficiency (w1 = 0.35, Benefit)
     C2: Off-Target Safety Score (w2 = 0.30, Benefit)
     C3: Cancer Relevance Factor (w3 = 0.20, Benefit - based on CDS exon lethality & mutation hotspot proximity)
     C4: GC Optimality Score (w4 = 0.15, Target 50% Gaussian Penalty)
   • Vector Normalization -> Weighted Normalized Matrix
   • Compute Positive Ideal (A+) and Negative Ideal (A-) Solutions
   • Compute Euclidean Separation Distances (S_i+, S_i-)
   • Calculate Relative Closeness: C_i = S_i- / (S_i+ + S_i-) ∈ [0, 1]
   • Sort and Rank Candidates with Detailed Provenance and Explanations
                      │
                      ▼
[Interactive Presentation & Audit Export (React Dashboard, FASTA, CSV, PDF)]
```

---

## D. Machine Learning Pipeline Architecture

```
                                  +-------------------------------------------------------------+
                                  |           RAW TRAINING DATA: Doench 2016 Dataset            |
                                  |   (~40,000 sgRNAs targeting Human & Mouse genes with assay  |
                                  |     activity logs, sequence contexts, and knockout scores)   |
                                  +------------------------------+------------------------------+
                                                                 |
                                                                 v
                                  +-------------------------------------------------------------+
                                  |                 DATA PREPROCESSING & SPLIT                  |
                                  |  - Deduplication & Quality Control Filter                    |
                                  |  - Target Normalization: MinMax / Rank Percentile [0, 1]    |
                                  |  - Gene-disjoint Stratified Split: Train (70%), Val (15%),  |
                                  |    Test (15%) [Prevents gene-level data leakage]            |
                                  +------------------------------+------------------------------+
                                                                 |
                                   +-----------------------------+-----------------------------+
                                   |                                                           |
                                   v                                                           v
+----------------------------------------------------+       +----------------------------------------------------+
|               BRANCH A: DEEP LEARNING              |       |             BRANCH B: FEATURE ENGINEERING          |
|  - Sequence: 30-nt context (4nt + 20nt + 3nt + 3nt)|       |  - 105 Engineered Biological & Physical Features:  |
|  - Encoding: One-Hot (4 x 30 matrix)               |       |    * Positional Single Nucleotides (28)            |
|  - 1D Convolutional Neural Network (PyTorch)       |       |    * Positional Dinucleotides (56)                |
|  - Residual connections + Dropout regularization   |       |    * Global GC & Regional GC fractions (8)        |
|  - Loss: MSE + Cosine Similarity Regularization    |       |    * Thermodynamic & Folding Proxy Metrics (8)    |
|  - Output: CNN Efficiency Score (S_CNN)            |       |    * PAM Proximal / Seed Properties (5)            |
+----------------------------------------------------+       |  - Model: Tuned XGBoost Regressor                  |
                           |                                 |  - Loss: reg:squarederror + Feature Subsampling    |
                           |                                 |  - Output: XGBoost Efficiency Score (S_XGB)        |
                           |                                 +----------------------------------------------------+
                           |                                                           |
                           +-----------------------------+-----------------------------+
                                                         |
                                                         v
                                  +-------------------------------------------------------------+
                                  |                 META-LEARNER ENSEMBLE                      |
                                  |  - Ridge / Stacking Linear Regressor with Non-Negativity     |
                                  |  - Final Score = α * S_CNN + β * S_XGB + γ                  |
                                  |  - Calibrated against Holdout Test Set                      |
                                  +------------------------------+------------------------------+
                                                                 |
                                                                 v
                                  +-------------------------------------------------------------+
                                  |            RIGOROUS SCIENTIFIC EVALUATION METRICS           |
                                  |  - Spearman Rank Correlation (ρ_s)                          |
                                  |  - Pearson Correlation Coefficient (r)                      |
                                  |  - Mean Absolute Error (MAE) & Root Mean Squared Error(RMSE)|
                                  |  - Coefficient of Determination (R²)                        |
                                  |  - Classification ROC-AUC (Top-Quartile Activity Binarized) |
                                  +-------------------------------------------------------------+
```

---

## E. CNN Architecture (PyTorch)

### 1. Input Specification
* **Context Length**: 30 nucleotides (4-nt 5' upstream + 20-nt guide protospacer + 3-nt PAM [NGG] + 3-nt 3' downstream).
* **Representation**: One-hot matrix of shape $(B, 4, 30)$ where channels represent $[A, C, G, T]$.

### 2. Layer-by-Layer Topology
```
Input (Shape: [Batch, 4, 30])
  │
  ├──> Conv1D Layer 1: 64 filters, kernel_size=3, padding=1, stride=1
  │    ├──> BatchNorm1D(64)
  │    ├──> LeakyReLU(negative_slope=0.1)
  │    └──> Spatial Dropout1D(p=0.15)
  │
  ├──> Conv1D Layer 2: 128 filters, kernel_size=5, padding=2, stride=1
  │    ├──> BatchNorm1D(128)
  │    ├──> LeakyReLU(negative_slope=0.1)
  │    └──> MaxPool1D(kernel_size=2, stride=2)  --> Output shape: [Batch, 128, 15]
  │
  ├──> Conv1D Layer 3 (Residual Bottleneck): 128 filters, kernel_size=3, padding=1
  │    ├──> BatchNorm1D(128)
  │    ├──> LeakyReLU(negative_slope=0.1)
  │    └──> Add Residual: Input + Conv3_out
  │
  ├──> Global Average Pooling 1D + Global Max Pooling 1D Concatenation --> Shape: [Batch, 256]
  │
  ├──> Fully Connected Layer 1: Linear(256, 128)
  │    ├──> BatchNorm1D(128)
  │    ├──> ReLU()
  │    └──> Dropout(p=0.30)
  │
  ├──> Fully Connected Layer 2: Linear(128, 32)
  │    ├──> ReLU()
  │    └──> Dropout(p=0.20)
  │
  └──> Output Layer: Linear(32, 1) -> Sigmoid() --> Final CNN Prediction ∈ [0.0, 1.0]
```

### 3. Hyperparameters & Optimization
* **Optimizer**: AdamW (Learning Rate: $1 \times 10^{-3}$, Weight Decay: $1 \times 10^{-4}$)
* **Scheduler**: CosineAnnealingWarmRestarts ($T_0=10, T_{mult}=2$)
* **Batch Size**: 128
* **Epochs**: 60 (with early stopping patience of 8 on Validation Spearman correlation)

---

## F. XGBoost Architecture & Training Strategy

### 1. Model Configuration
* **Algorithm**: `xgboost.XGBRegressor` (Tree booster with histogram-based binning: `tree_method="hist"`)
* **Objective Function**: `reg:squarederror`
* **Base Metric**: Spearman rank correlation on validation folds.

### 2. Hyperparameters
```python
xgb_params = {
    "n_estimators": 450,
    "learning_rate": 0.035,
    "max_depth": 5,
    "min_child_weight": 6,
    "subsample": 0.85,
    "colsample_bytree": 0.75,
    "colsample_bylevel": 0.80,
    "gamma": 0.15,
    "reg_alpha": 0.05,
    "reg_lambda": 1.2,
    "random_state": 42,
    "n_jobs": -1
}
```

### 3. Cross-Validation Strategy
* **Gene-Stratified 5-Fold Cross-Validation**: To prevent sequence leakage, all guide RNAs targeting the same gene are grouped strictly into the same fold (`GroupKFold` over Gene IDs).

---

## G. Exact 105-Feature Engineering Strategy

Following and extending the Doench et al. (2016) Rule Set 2 and DeepCRISPR sequence modeling principles, exactly **105 numerical features** are extracted from the 30-nt extended context sequence ($N_{-4}N_{-3}N_{-2}N_{-1} \, [N_1 \dots N_{20}] \, N_{PAM1}N_{PAM2}N_{PAM3} \, N_{+1}N_{+2}N_{+3}$):

```
+-------------------------------------------------------------------------------------------------------+
| Category                                | Feature Count | Exact Description & Feature Indices         |
+-----------------------------------------+---------------+---------------------------------------------+
| 1. Position-Specific Single Nucleotide  | 28 features   | One-hot indicators for specific nucleotides |
|    (Doench Single-mer Hotspots)         | (Indices 0-27)| at key positions:                           |
|                                         |               | - Guide Pos 1..20 for key bases A/C/G/T     |
|                                         |               | - PAM-adjacent context (-1 to -4, +1 to +3) |
|                                         |               | - Strongly penalized poly-T (terminator)    |
|                                         |               |   and poly-G at positions 16-20.            |
+-----------------------------------------+---------------+---------------------------------------------+
| 2. Position-Specific Dinucleotides      | 56 features   | Selected consecutive dinucleotides:         |
|    (Doench Di-mer Interactions)         | (Indices 28-83| - Dinucleotide pairs at seed region (11-20) |
|                                         |               | - Dinucleotide pairs at PAM proximal site   |
|                                         |               | - Specific motif penalties (e.g., TT, GG,   |
|                                         |               |   CC, AA frequencies at critical junctions) |
+-----------------------------------------+---------------+---------------------------------------------+
| 3. Global & Regional GC Content         | 8 features    | - Global GC% of 20-nt guide                 |
|    Metrics                              | (Indices 84-91| - Seed GC% (positions 11 to 20, 10-nt)      |
|                                         |               | - PAM-distal GC% (positions 1 to 10)        |
|                                         |               | - 30-nt context GC%                         |
|                                         |               | - GC deviation from optimum (abs(GC - 0.50))|
|                                         |               | - GC content in 4-nt 5' flank               |
|                                         |               | - GC content in 3-nt 3' flank               |
|                                         |               | - GC balance ratio (Seed GC / Distal GC)    |
+-----------------------------------------+---------------+---------------------------------------------+
| 4. Thermodynamic & Structural Proxies   | 8 features    | - Melting Temperature Tm (nearest-neighbor) |
|                                         | (Indices 92-99| - Seed region Tm (positions 11-20)          |
|                                         |               | - Core PAM proximal Tm (positions 16-20)    |
|                                         |               | - Enthalpy ΔH estimate for guide-DNA duplex |
|                                         |               | - Entropy ΔS estimate                       |
|                                         |               | - Free Energy ΔG estimate                   |
|                                         |               | - Self-complementarity hairpin score proxy  |
|                                         |               | - Secondary structure penalty proxy         |
+-----------------------------------------+---------------+---------------------------------------------+
| 5. Sequence Complexity & Motif Flags    | 5 features    | - Maximum homopolymer run length (e.g. TTTT)|
|                                         | (Indices      | - Shannon Sequence Entropy of 20-nt guide   |
|                                         |  100-104)     | - Purine/Pyrimidine balance ratio (A+G)/(C+T|
|                                         |               | - Position of longest G-run                 |
|                                         |               | - G-quadruplex motif propensity indicator   |
+-----------------------------------------+---------------+---------------------------------------------+
| TOTAL ENGINEERED FEATURES               | 105 FEATURES  | EXACT FIXED FEATURE VECTOR LENGTH: 105      |
+-----------------------------------------+---------------+---------------------------------------------+
```

---

## H. Dataset Ingestion, Provenance & Validation Pipeline

### 1. Training Dataset: Doench 2016 CRISPR sgRNA Activity Dataset
* **Source**: Broad Institute CRISPR Activity Screens (Rule Set 2 paper: *Nat Biotechnol. 2016 Mar; 34(2): 184–191*).
* **Content**: ~40,000 sgRNAs targeting human genes (HCT116, 293T) and mouse genes with normalized log2 fold-change depletion/activation scores.
* **Storage Location**: `data/doench2016/raw_activity_data.csv` (downloaded via automated reproducible script `scripts/download_doench2016_dataset.py`).

### 2. Biological Validation Standards & No-Fabrication Guarantee
* The system **never synthesizes** training rows, model accuracy figures, or experimental benchmark values.
* The evaluation metrics displayed in the user interface reflect actual computed results on the holdout test set with detailed scatter plots and residual histograms.

---

## I. Stage 4: GRCh38 Off-Target & CFD Specificity Architecture

### 1. Genomic Reference & Alignment Strategy
* **Reference Genome**: Human Reference Genome Assembly GRCh38.p14.
* **Search Tools Supported**:
  1. **Bowtie2**: Fast seed-and-extend index matching up to 3 mismatches in the 20-nt guide.
  2. **BLAST+ (blastn-short)**: Sensitive alignment with word size 7 for short oligonucleotide matching.

### 2. Cutting Frequency Determination (CFD) Scoring
For each off-target site identified, the CFD score calculates cleavage probability based on experimental mismatch position and identity matrices:
$$\text{CFD}_{\text{site}} = \left( \prod_{p \in \text{Mismatches}} M(p, r_p, a_p) \right) \times P(\text{PAM})$$
where:
* $M(p, r_p, a_p)$ is the mismatch weight at guide position $p$ between reference base $r_p$ and off-target base $a_p$.
* $P(\text{PAM})$ is the PAM penalty factor (e.g., $NGG = 1.0$, $NAG = 0.259$, $NGA = 0.069$).

### 3. Cumulative Specificity Score
$$\text{Specificity Score} = \frac{100}{100 + \sum_{k=1}^{K} \text{CFD}_k} \in [0, 100]$$
Normalized Off-Target Safety Score for TOPSIS: $O = \frac{\text{Specificity Score}}{100} \in [0.0, 1.0]$.

### 4. Handling `GENOME_NOT_AVAILABLE`
* When running in **REAL MODE** without local Bowtie2/BLAST GRCh38 index files:
  1. The API responds with status: `"GENOME_NOT_AVAILABLE"`.
  2. Detailed instructions for downloading GRCh38 and building indices via `scripts/download_grch38_index.py` are returned.
  3. The frontend displays an explicit diagnostic banner with genome setup instructions.
* In **DEMO MODE**, pre-computed deterministic off-target fixtures for the 9 target cancer genes are loaded automatically.

---

## J. Stage 5: TOPSIS Multi-Criteria Decision Ranking Engine

### 1. Mathematical Formulation
Given $m$ candidate guide RNAs evaluated against $n=4$ criteria:
1. **$C_1$: On-Target Efficiency Score ($E$)** (Weight $w_1 = 0.35$, Maximization)
2. **$C_2$: Off-Target Safety Score ($O$)** (Weight $w_2 = 0.30$, Maximization)
3. **$C_3$: Cancer Relevance Factor ($R$)** (Weight $w_3 = 0.20$, Maximization)
   * Computed based on functional CDS exon location, essentiality index (DepMap CRISPR dependency), and mutation hotspot targeting.
4. **$C_4$: GC-Content Optimality Score ($G$)** (Weight $w_4 = 0.15$, Maximization)
   * $G = 1.0 - \min\left(1.0, \, 2 \cdot |\text{GC} - 0.50|\right)$

### 2. Standard TOPSIS 8-Step Algorithm
1. **Decision Matrix Formation**:
   $$X = [x_{ij}]_{m \times 4} \quad (i = 1 \dots m, \, j = 1 \dots 4)$$
2. **Vector Normalization**:
   $$r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{k=1}^{m} x_{kj}^2}}$$
3. **Weighted Normalized Decision Matrix**:
   $$v_{ij} = w_j \cdot r_{ij} \quad \text{where } \sum_{j=1}^4 w_j = 1.00$$
4. **Positive Ideal Solution ($A^+$) and Negative Ideal Solution ($A^-$)**:
   $$A^+ = (\max_i v_{i1}, \max_i v_{i2}, \max_i v_{i3}, \max_i v_{i4})$$
   $$A^- = (\min_i v_{i1}, \min_i v_{i2}, \min_i v_{i3}, \min_i v_{i4})$$
5. **Euclidean Distance to Ideal Solutions**:
   $$S_i^+ = \sqrt{\sum_{j=1}^4 (v_{ij} - v_j^+)^2}, \quad S_i^- = \sqrt{\sum_{j=1}^4 (v_{ij} - v_j^-)^2}$$
6. **Relative Closeness Coefficient**:
   $$C_i = \frac{S_i^-}{S_i^+ + S_i^-} \quad (0 \le C_i \le 1)$$
7. **Ranking**:
   Sort guides in descending order of $C_i$.
8. **Provenance & Traceability**:
   Store intermediate matrices ($X, R, V$), distances ($S^+, S^-$), and criteria breakdown for each candidate.

---

## K. PostgreSQL Database Schema

```sql
-- PostgreSQL 15+ Schema for Gene-Cure AI Platform

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table 1: Cancer Target Genes Registry
CREATE TABLE cancer_genes (
    gene_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    cancer_types TEXT[] NOT NULL, -- {'Breast cancer', 'Lung cancer', 'Liver cancer'}
    ncbi_gene_id VARCHAR(50) NOT NULL,
    ensembl_id VARCHAR(50) NOT NULL,
    chromosome VARCHAR(10) NOT NULL,
    strand CHAR(1) NOT NULL CHECK (strand IN ('+', '-')),
    genomic_start BIGINT NOT NULL,
    genomic_end BIGINT NOT NULL,
    canonical_transcript_id VARCHAR(50) NOT NULL,
    cds_sequence TEXT NOT NULL,
    full_transcript_sequence TEXT NOT NULL,
    cancer_relevance_summary TEXT NOT NULL,
    depmap_dependency_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Pipeline Execution Runs
CREATE TABLE pipeline_runs (
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gene_id UUID REFERENCES cancer_genes(gene_id) ON DELETE CASCADE,
    execution_mode VARCHAR(20) NOT NULL CHECK (execution_mode IN ('REAL_MODE', 'DEMO_MODE')),
    status VARCHAR(30) NOT NULL CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'GENOME_NOT_AVAILABLE')),
    weights_json JSONB NOT NULL, -- {w_on_target: 0.35, w_off_target: 0.30, w_cancer: 0.20, w_gc: 0.15}
    total_candidates_found INT DEFAULT 0,
    top_candidates_retained INT DEFAULT 0,
    execution_time_ms INT,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: Candidate Guide RNAs
CREATE TABLE guide_rnas (
    guide_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    gene_id UUID REFERENCES cancer_genes(gene_id) ON DELETE CASCADE,
    protospacer_sequence VARCHAR(20) NOT NULL,
    pam_sequence VARCHAR(3) NOT NULL,
    context_30nt_sequence VARCHAR(30) NOT NULL,
    strand CHAR(1) NOT NULL CHECK (strand IN ('+', '-')),
    genomic_start BIGINT NOT NULL,
    genomic_end BIGINT NOT NULL,
    exon_number INT,
    gc_percentage FLOAT NOT NULL,
    has_poly_t_terminator BOOLEAN NOT NULL DEFAULT FALSE,
    self_complementarity_score FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 4: On-Target Efficiency Predictions
CREATE TABLE on_target_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    guide_id UUID UNIQUE REFERENCES guide_rnas(guide_id) ON DELETE CASCADE,
    cnn_score FLOAT NOT NULL,
    xgboost_score FLOAT NOT NULL,
    ensemble_score FLOAT NOT NULL,
    feature_vector_105 JSONB,
    model_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 5: Off-Target Analysis & Specificity
CREATE TABLE off_target_evaluations (
    evaluation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    guide_id UUID UNIQUE REFERENCES guide_rnas(guide_id) ON DELETE CASCADE,
    search_tool_used VARCHAR(30) NOT NULL, -- 'Bowtie2', 'BLAST+', 'DEMO_FIXTURE'
    reference_genome VARCHAR(50) NOT NULL DEFAULT 'GRCh38.p14',
    total_off_targets_found INT NOT NULL DEFAULT 0,
    mismatch_0_count INT NOT NULL DEFAULT 0,
    mismatch_1_count INT NOT NULL DEFAULT 0,
    mismatch_2_count INT NOT NULL DEFAULT 0,
    mismatch_3_count INT NOT NULL DEFAULT 0,
    cumulative_cfd_score FLOAT NOT NULL,
    specificity_score FLOAT NOT NULL, -- 0.0 to 100.0
    normalized_safety_score FLOAT NOT NULL, -- 0.0 to 1.0
    detailed_sites JSONB, -- Array of [{chr, pos, strand, mismatches, cfd_score, gene_overlap}]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 6: TOPSIS Multi-Criteria Rankings
CREATE TABLE topsis_rankings (
    ranking_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    guide_id UUID REFERENCES guide_rnas(guide_id) ON DELETE CASCADE,
    on_target_criterion FLOAT NOT NULL,
    off_target_criterion FLOAT NOT NULL,
    cancer_relevance_criterion FLOAT NOT NULL,
    gc_optimality_criterion FLOAT NOT NULL,
    distance_positive_ideal FLOAT NOT NULL,
    distance_negative_ideal FLOAT NOT NULL,
    closeness_score FLOAT NOT NULL,
    final_rank INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Optimization Indexes
CREATE INDEX idx_cancer_genes_symbol ON cancer_genes(symbol);
CREATE INDEX idx_guide_rnas_gene_id ON guide_rnas(gene_id);
CREATE INDEX idx_guide_rnas_run_id ON guide_rnas(run_id);
CREATE INDEX idx_topsis_rankings_run_rank ON topsis_rankings(run_id, final_rank);
```

---

## L. FastAPI REST API Endpoint Design

```
+-------------------------------------------------------------------------------------------------------+
| HTTP Method & Path                         | Request Body / Parameters        | Response Payload      |
+-------------------------------------------------------------------------------------------------------+
| GET  /api/v1/health                        | None                             | Health & Mode Status  |
| GET  /api/v1/cancer-genes                  | ?cancer_type=Breast|Lung|Liver   | List[CancerGeneSchema]|
| GET  /api/v1/cancer-genes/{symbol}         | Path: symbol (e.g. BRCA1)        | DetailedGeneSchema    |
| POST /api/v1/pipeline/execute              | PipelineExecutionRequest         | PipelineRunResult     |
| GET  /api/v1/pipeline/runs/{run_id}        | Path: run_id                     | FullPipelineRunStatus |
| POST /api/v1/guide-design/scan             | SequenceScanRequest              | List[CandidateGuide]  |
| POST /api/v1/on-target/predict             | OnTargetPredictRequest           | OnTargetScoreResult   |
| POST /api/v1/off-target/analyze            | OffTargetAnalyzeRequest          | OffTargetScoreResult  |
| POST /api/v1/topsis/rank                   | TOPSISRankRequest (custom w)     | TOPSISRankResponse    |
| GET  /api/v1/export/run/{run_id}/fasta     | Path: run_id, ?top_n=10          | Downloadable FASTA    |
| GET  /api/v1/export/run/{run_id}/csv       | Path: run_id                     | Downloadable CSV      |
| GET  /api/v1/export/run/{run_id}/pdf       | Path: run_id                     | PDF Report Stream     |
| GET  /api/v1/model-metrics/on-target       | None                             | ModelEvaluationReport |
+-------------------------------------------------------------------------------------------------------+
```

---

## M. React Components & User Interface Architecture

```
Frontend Component Hierarchy (React 18 + TypeScript + Vite + TailwindCSS + Recharts)
│
├── App.tsx (Root Provider, Banner for In-Silico Scientific Disclaimer, Mode Indicator)
│   │
│   ├── Navbar.tsx (Navigation, System Mode Badge [REAL/DEMO], Target Cancer Selector)
│   │
│   └── AppRouter.tsx (Page Routing)
│       │
│       ├── HomePage.tsx
│       │   ├── HeroSection.tsx (Platform overview, 5-stage pipeline diagram)
│       │   ├── CancerFocusSection.tsx (Breast, Lung, Liver cancer molecular targets)
│       │   └── SystemArchitectureOverview.tsx
│       │
│       ├── GeneCatalogPage.tsx
│       │   ├── CancerTypeFilter.tsx
│       │   ├── GeneCardGrid.tsx (BRCA1, HER2, TP53, EGFR, KRAS, ALK, CTNNB1, AXIN1, TERT)
│       │   └── GeneProvenanceModal.tsx (NCBI, Ensembl, CDS Sequence Viewer)
│       │
│       ├── GuideDesignStudioPage.tsx (Stage 1 & 2)
│       │   ├── SequenceViewer.tsx (Interactive Exon map, forward & reverse-complement)
│       │   ├── PAMHighlightTrack.tsx (5'-NGG-3' motifs in-situ)
│       │   ├── GuideCandidateTable.tsx (Sortable, GC% filter, poly-T warning flags)
│       │   └── CandidateDetailDrawer.tsx
│       │
│       ├── OnTargetEvaluationPage.tsx (Stage 3)
│       │   ├── HybridModelScoreGauge.tsx (CNN + XGBoost ensemble blend)
│       │   ├── SequenceLogoViewer.tsx (Positional nucleotide contribution)
│       │   ├── FeatureImportance105Chart.tsx (XGBoost SHAP/Gain bar plot via Recharts)
│       │   └── CNNActivationHeatmap.tsx
│       │
│       ├── OffTargetSafetyPage.tsx (Stage 4)
│       │   ├── GenomeAvailabilityAlert.tsx (Displays setup instructions if missing)
│       │   ├── SpecificityScoreCard.tsx (100 / (100 + Σ CFD))
│       │   ├── GenomicMismatchTable.tsx (Seed vs. Non-seed mismatches)
│       │   └── ChromosomeLocusMap.tsx (GRCh38 off-target distribution)
│       │
│       ├── TOPSISRankingPage.tsx (Stage 5)
│       │   ├── WeightCustomizerSlider.tsx (Default 35/30/20/15 with real-time normalization)
│       │   ├── RadarSeparationChart.tsx (Positive vs. Negative Ideal Solution distances)
│       │   ├── RankedGuideTable.tsx (Final rank, Closeness score C_i, Export checkboxes)
│       │   └── SensitivityAnalysisView.tsx (Weight perturbation impact)
│       │
│       ├── PipelineWizardPage.tsx (Unified Full 5-Stage Execution)
│       │   ├── StepperProgressHeader.tsx
│       │   ├── LiveExecutionLog.tsx
│       │   └── ComprehensiveResultsSummary.tsx
│       │
│       └── ModelValidationReportPage.tsx
│           ├── ActualValidationMetricsTable.tsx (Spearman, Pearson, MAE, RMSE, R²)
│           ├── ResidualScatterPlot.tsx
│           └── ScientificReferencesSection.tsx (Doench 2016, DeepCRISPR, Tandon 2024, Bhat 2022)
```

---

## N. Comprehensive Testing Strategy

```
+-------------------------------------------------------------------------------------------------------+
| Test Level      | Scope & Target                                    | Verification Method             |
+-------------------------------------------------------------------------------------------------------+
| 1. Unit Tests   | - Guide scanning (NGG, reverse complement)        | Pytest with synthetic & known   |
|                 | - 105-feature extraction length & value invariants| positive control sequences      |
|                 | - CFD scoring against published Doench matrices   | (e.g. validated EMX1/VEGFA loci)|
|                 | - TOPSIS ranking algorithm math & edge cases      |                                 |
+-------------------------------------------------------------------------------------------------------+
| 2. ML Tests     | - PyTorch CNN input/output dimension assertions   | Pytest + Torch test harness     |
|                 | - XGBoost 105-feature vector alignment checks     | Strict feature name & index     |
|                 | - No NaN / Infinite outputs on random sequences   | validation                      |
|                 | - Model weight loading integrity                  |                                 |
+-------------------------------------------------------------------------------------------------------+
| 3. Integration  | - Full 5-stage pipeline execution in DEMO MODE    | Pytest async HTTP client        |
|                 | - Full 5-stage pipeline execution in REAL MODE    | (TestClient) validating DB state|
|                 | - GRCh38 missing genome error handling            | and API response contracts      |
|                 | - FASTA / CSV export formatting                   |                                 |
+-------------------------------------------------------------------------------------------------------+
| 4. Frontend UI  | - Component rendering & user interaction          | Vitest + React Testing Library  |
|                 | - Slider weight normalization invariants          | UserEvent simulations           |
|                 | - Mode banner & disclaimer modal visibility       |                                 |
+-------------------------------------------------------------------------------------------------------+
| 5. End-to-End   | - End-to-end user journey from Gene selection     | Playwright / Cypress headless   |
|                 |   to Ranked Guide export                          | browser testing                 |
+-------------------------------------------------------------------------------------------------------+
```

---

## O. DEMO MODE Architecture & Deterministic Fixtures

To ensure seamless demonstration, grading, and testing without requiring users to download hundreds of gigabytes of GRCh38 indices:
1. **Deterministic Fixture Store**: `backend/app/fixtures/` contains pre-computed, verified results for the 9 target cancer genes (`BRCA1`, `HER2`, `TP53`, `EGFR`, `KRAS`, `ALK`, `CTNNB1`, `AXIN1`, `TERT`).
2. **Execution Flow**:
   * When `EXECUTION_MODE=DEMO_MODE` or when genomic indices are absent, the platform serves cached biological fixtures.
   * Fixtures contain real canonical transcripts, real SpCas9 guide candidates, genuine ML predictions, and pre-computed GRCh38 off-target alignments.
   * **No random numbers are generated**: Results remain 100% deterministic and reproducible across all runs.
3. **Transparent Mode Indication**:
   * Every API response includes `mode: "DEMO_MODE"` or `mode: "REAL_MODE"`.
   * The UI persistently displays an amber `DEMO MODE` badge with full explanation or a green `REAL MODE` badge.

---

## P. Deployment & DevOps Strategy

1. **Local Development (Single Command)**:
   * `docker-compose up --build` launches PostgreSQL, Redis, FastAPI Backend, and Vite Frontend.
2. **Cloud Deployment**:
   * **Backend**: Containerized on **Railway** / Render with persistent volume mount for model weights.
   * **Frontend**: Optimized static build deployed on **Vercel** with CDN edge caching.
   * **Database**: Managed **PostgreSQL** instance on Railway / Supabase.
3. **Environment Configuration**:
   ```env
   # Backend .env
   APP_ENV=production
   EXECUTION_MODE=DEMO_MODE # Switch to REAL_MODE when indices present
   DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/genecureai
   GRCH38_BOWTIE2_INDEX_PATH=/data/references/grch38/bowtie2_index
   BLAST_DB_PATH=/data/references/grch38/blast_db
   CORS_ORIGINS=["http://localhost:5173", "https://genecureai.vercel.app"]
   ```

---

## Q. Phased Project Development Plan

```
+-------------------------------------------------------------------------------------------------------+
| Phase                     | Key Deliverables                                                          |
+-------------------------------------------------------------------------------------------------------+
| Phase 1: Foundation &     | - PostgreSQL schema creation and SQLAlchemy models                        |
| Data Infrastructure       | - Canonical sequence curation & provenance for 9 cancer genes             |
|                           | - Deterministic demo fixtures generation                                  |
+-------------------------------------------------------------------------------------------------------+
| Phase 2: Core Bio & ML    | - SpCas9 guide scanner (20nt + NGG, forward & reverse complement)         |
| Engine Development        | - 105-feature extraction engine (Doench Rule Set 2 compliance)            |
|                           | - PyTorch CNN model training & XGBoost model training on Doench 2016      |
|                           | - Meta-learner stacking and model evaluation suite                        |
+-------------------------------------------------------------------------------------------------------+
| Phase 3: Off-Target &     | - Bowtie2 / BLAST+ alignment wrapper with GENOME_NOT_AVAILABLE fallback  |
| TOPSIS Ranking Engine     | - CFD scoring matrix implementation & cumulative specificity scoring      |
|                           | - Complete TOPSIS multi-criteria ranking engine with dynamic weights      |
+-------------------------------------------------------------------------------------------------------+
| Phase 4: API & Backend    | - FastAPI routers for all 5 stages                                        |
| Integration               | - Pipeline orchestrator and async job execution                           |
|                           | - Comprehensive Pytest unit and integration test suite                    |
+-------------------------------------------------------------------------------------------------------+
| Phase 5: Modern Frontend  | - React + TypeScript + TailwindCSS + Recharts application                 |
| Development               | - Interactive genome and candidate guide viewers                          |
|                           | - On-target ML explainability & TOPSIS ranking sensitivity studio         |
|                           | - Audit trail, FASTA/CSV/PDF export, scientific disclaimer banner         |
+-------------------------------------------------------------------------------------------------------+
| Phase 6: System E2E       | - Docker containerization and docker-compose orchestration                |
| Verification & Deployment | - End-to-end integration tests & verification                             |
|                           | - Final project documentation & academic walkthrough                       |
+-------------------------------------------------------------------------------------------------------+
```

---
*End of Master Implementation Plan.*
