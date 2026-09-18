# TCGA Cancer Relevance Data Audit Report

**Audit Date**: 2026-08-15  
**Data Source Path**: `C:\Users\GeneCureAI\results\cancer_relevance_scores.csv`  
**Data Provenance**: Derived from The Cancer Genome Atlas (TCGA) RNA-seq STAR Counts across Breast, Lung, and Liver cancer cohorts.

---

## 1. Schema & Summary

- **Total Records**: 9 rows
- **Columns**:
  1. `cancer_type` (string): Primary tumor tissue ('Breast', 'Lung', 'Liver')
  2. `gene` (string): HGNC gene symbol ('BRCA1', 'ERBB2', 'TP53', 'EGFR', 'KRAS', 'ALK', 'CTNNB1', 'AXIN1', 'TERT')
  3. `mean_expr` (float): Mean normalized RNA-seq read count (STAR Counts) across cohort samples
  4. `cancer_relevance_score` (float): Min-max normalized relative expression score within the tumor cohort in $[0.0, 1.0]$

---

## 2. Complete Verified Dataset Contents

| Cancer Type | Gene Symbol | Alias (UI) | Mean Expression (STAR Counts) | Cancer Relevance Score |
| :--- | :--- | :--- | :--- | :--- |
| **Breast** | `BRCA1` | BRCA1 | 1,304.21 | **0.0000** |
| **Breast** | `ERBB2` | HER2 | 46,982.49 | **1.0000** |
| **Breast** | `TP53` | TP53 | 4,935.74 | **0.0795** |
| **Lung** | `EGFR` | EGFR | 15,359.37 | **1.0000** |
| **Lung** | `KRAS` | KRAS | 3,723.35 | **0.2392** |
| **Lung** | `ALK` | ALK | 65.85 | **0.0000** |
| **Liver** | `CTNNB1` | CTNNB1 | 10,760.09 | **1.0000** |
| **Liver** | `AXIN1` | AXIN1 | 1,225.60 | **0.0917** |
| **Liver** | `TERT` | TERT | 263.37 | **0.0000** |

---

## 3. Metric Definition & Normalization

The **Cancer Relevance Score** reflects the relative RNA expression level of the target oncogene/tumor suppressor within its primary tumor indication cohort:
$$\text{Cancer Relevance Score} = \frac{\text{mean\_expr} - \min(\text{mean\_expr}_{\text{cohort}})}{\max(\text{mean\_expr}_{\text{cohort}}) - \min(\text{mean\_expr}_{\text{cohort}})}$$

- **Scientific Meaning**: A relative transcript abundance proxy within the specific tumor type indication.
- **Distinction**: `0.0000` reflects the lowest expressing target in the verified set (e.g. BRCA1 in breast, ALK in lung, TERT in liver), not a missing value.
- **Gene Alias Handling**: `HER2` is canonically mapped to `ERBB2` with identical score lookup.
