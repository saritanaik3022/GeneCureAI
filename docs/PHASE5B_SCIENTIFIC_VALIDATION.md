# Phase 5B Scientific Validation & Methodology Audit

**Report Date**: 2026-08-15  
**Project**: Gene-Cure AI  
**Scope**: Scientific methodology, mathematical derivations, TOPSIS formulation, missing data handling, and limitations.

---

## 1. Mathematical Formulation of TOPSIS Engine

The platform implements the Technique for Order Preference by Similarity to Ideal Solution (TOPSIS) multi-criteria decision algorithm (Hwang & Yoon, 1981).

### Step 1: Decision Matrix Construction
For $m$ candidate gRNAs evaluated across $n=4$ criteria:
$$X = \begin{pmatrix} x_{11} & x_{12} & x_{13} & x_{14} \\ x_{21} & x_{22} & x_{23} & x_{24} \\ \vdots & \vdots & \vdots & \vdots \\ x_{m1} & x_{m2} & x_{m3} & x_{m4} \end{pmatrix}$$
where:
- $C_1$: On-target efficiency predicted by Hybrid 1D-CNN + XGBoost ensemble ($\in [0.0, 1.0]$)
- $C_2$: Off-target safety score derived from Bowtie2 alignment & CFD matrix ($\in [0.0, 1.0]$)
- $C_3$: TCGA Cancer relevance expression score ($\in [0.0, 1.0]$)
- $C_4$: GC content optimality score ($1.0 - \min(1.0, 2.0 \times |\text{GC} - 0.50|)$)

### Step 2: Vector Normalization
$$r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{k=1}^m x_{kj}^2}}, \quad i=1,\dots,m, \quad j=1,\dots,4$$

### Step 3: Weighted Normalized Matrix
$$v_{ij} = w_j \cdot r_{ij}, \quad \text{where } \sum_{j=1}^4 w_j = 0.35 + 0.30 + 0.20 + 0.15 = 1.00$$

### Step 4: Positive ($A^+$) and Negative ($A^-$) Ideal Solutions
Since all four criteria are formulated as benefit criteria (higher is better):
$$A^+ = \{v_1^+, v_2^+, v_3^+, v_4^+\} = \{\max_i v_{i1}, \max_i v_{i2}, \max_i v_{i3}, \max_i v_{i4}\}$$
$$A^- = \{v_1^-, v_2^-, v_3^-, v_4^-\} = \{\min_i v_{i1}, \min_i v_{i2}, \min_i v_{i3}, \min_i v_{i4}\}$$

### Step 5: Separation Distances
Euclidean distance to positive ideal $A^+$:
$$S_i^+ = \sqrt{\sum_{j=1}^4 (v_{ij} - v_j^+)^2}$$
Euclidean distance to negative ideal $A^-$:
$$S_i^- = \sqrt{\sum_{j=1}^4 (v_{ij} - v_j^-)^2}$$

### Step 6: Relative Closeness & Final Ranking
$$C_i = \frac{S_i^-}{S_i^+ + S_i^-}, \quad C_i \in [0.0, 1.0]$$
Candidates are ranked in descending order of $C_i$.

---

## 2. Missing Data Policy

- **No Silent Imputation**: If any required criterion ($C_1, C_2, C_3, C_4$) cannot be computed or retrieved, the candidate is marked `INCOMPLETE_FOR_RANKING`.
- **Explicit Status Messages**:
  - `MODEL_NOT_READY`: On-target model weights missing
  - `GENOME_INDEX_NOT_AVAILABLE`: Bowtie2 GRCh38 index missing
  - `CANCER_RELEVANCE_NOT_AVAILABLE`: TCGA gene expression data missing
- **Zero Fabrication Guarantee**: The system never substitutes artificial random values or default averages for missing criteria.

---

## 3. Mandatory Scientific Disclaimers

> [!IMPORTANT]
> **COMPUTATIONAL PREDICTION DISCLAIMER**:
> This platform provides in-silico computational predictions and is not a substitute for experimental validation. All predicted on-target efficiencies, off-target cleavage probabilities, and TOPSIS rankings are computational estimates requiring empirical wet-lab validation (e.g., T7E1 assays, GUIDE-seq, or amplicon sequencing) prior to therapeutic or experimental application.
