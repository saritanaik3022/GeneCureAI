# Model Performance & Benchmark Evaluation

## Overview
Evaluation benchmarks for on-target CRISPR guide RNA efficiency prediction on the held-out test split of the **Doench 2016 Rule Set 2** dataset (531 samples).

- **Ground Truth Target**: `score_drug_gene_rank` (Doench experimental cleavage activity)
- **Feature Specification**: `gene-cure-v1-105` (105 engineered features)
- **Test Set Size**: 531 records (10% held-out test set, seed=42)

---

## Model Comparison Summary

| Model | Spearman (ρ) | Pearson (r) | MAE | RMSE | R² |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PyTorch 1D-CNN** | **0.6473** | **0.6544** | **0.1692** | **0.2298** | **0.3982** |
| **XGBoost (105 Features)** | **0.5985** | **0.6133** | **0.1941** | **0.2353** | **0.3688** |
| **Hybrid (CNN + XGBoost)** | **0.6561** | **0.6660** | **0.1645** | **0.2241** | **0.4272** |

---

## Architectural Insights

1. **PyTorch 1D-CNN**: Extracts high-order local and long-range nucleotide motifs (3-mer and 5-mer convolutional filters) directly from $(4, 30)$ one-hot representations.
2. **XGBoost 105-Feature Booster**: Leverages 28 single-mer position indicators, 56 dinucleotide interaction features, 8 regional GC metrics, 8 nearest-neighbor thermodynamic stacking proxies ($\Delta G^\circ_37$ / $T_m$), and 5 structural motif flags.
3. **Hybrid Stacking Meta-Learner**: Combines the 64-dimensional sequence embeddings from the 1D-CNN with the 105 engineered biophysical features ($169$ total input dimensions), capturing both spatial sequence motifs and thermodynamic binding free energies.

---

## Verification & Artifacts
All models were trained on the real Doench 2016 dataset and evaluated on the same test split:
- CNN Artifact: `ml/models/cnn/cnn_best.pt`
- XGBoost Artifact: `ml/models/xgboost/xgboost_model.json`
- Hybrid Artifact: `ml/models/hybrid/hybrid_model.json`
