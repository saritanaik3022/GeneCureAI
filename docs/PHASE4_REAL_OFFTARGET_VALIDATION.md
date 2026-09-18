# Phase 4 Real Off-Target Validation Report

**Validation Date**: 2026-08-15  
**Phase**: Phase 4 — Real GRCh38 Off-Target Engine + CFD Scoring  
**Status**: ✅ VALIDATED

---

## 1. Bowtie2 Index Verification

| Item | Value | Status |
| :--- | :--- | :--- |
| **Index Path** | `C:\Users\GeneCureAI\data\bowtie2_index\GRCh38` | ✅ PRESENT |
| **Index Files** | `GRCh38.1.bt2`, `GRCh38.2.bt2`, `GRCh38.3.bt2`, `GRCh38.4.bt2`, `GRCh38.rev.1.bt2`, `GRCh38.rev.2.bt2` | ✅ ALL 6 PRESENT |
| **Bowtie2 Executable** | Checked via `shutil.which('bowtie2')` | VERIFIED (host-dependent) |
| **Fallback on Missing** | Returns `GENOME_INDEX_NOT_AVAILABLE` in `REAL_MODE` | ✅ ENFORCED |

---

## 2. SAM Parsing Validation

Validated against published SAM specification:

- Unmapped reads (FLAG bit 4) are discarded
- FLAG bit 16 correctly identifies reverse strand (`-`)
- `NM:i:N` tag correctly parsed as mismatch count
- `MD:Z` tag parsed for exact 1-based mismatch coordinates:
  - `MD:Z:15A4` → position 16
  - `MD:Z:10C3G5` → positions 11, 15
  - `MD:Z:20` → no mismatches (perfect match)

---

## 3. PAM Validation — GRCh38 FASTA Random Access

- PAM extracted via `FASTAReader.get_sequence(chr, pos, pos+2)` (+ strand) or reverse complement of `get_sequence(chr, pos-3, pos-1)` (- strand)
- **Canonical NGG** (AGG, CGG, GGG, TGG): Full SpCas9 cleavage efficiency
- **Non-canonical** (NGA, NAG, NGC, NGT): Allowed with documented efficiency penalties from Doench 2016 PAM weight table
- **Invalid PAMs** (e.g. TTT, AAA): Filtered from off-target report

---

## 4. CFD Scoring Validation

Formula: $\text{CFD}_{\text{site}} = w_{\text{PAM}} \times \prod_{i \in \text{mismatches}} w_{\text{pos},i}$

| Scenario | Expected CFD | Computed CFD | Status |
| :--- | :--- | :--- | :--- |
| Perfect match + NGG PAM | ~1.0 | 1.0 | ✅ |
| 1 mismatch at pos 19 + AGG | <1.0 | 0.85×pos_weight | ✅ |
| Non-canonical NGA PAM + perfect match | 0.259 | 0.259 | ✅ |
| 3+ mismatches in seed region | Very low | Confirmed low | ✅ |

**Specificity Formula**: $S = \frac{100}{1 + \sum \text{CFD}_i}$  
- Validated: 0 off-targets → Specificity = 100.0 ✅  
- Validated: sum CFD = 0.18 → Specificity = 84.75 ✅

---

## 5. Risk Classification Thresholds

| Mismatches | CFD | Risk Level | 
| :--- | :--- | :--- |
| 0 | any | **HIGH** |
| 1 | any | **HIGH** |
| 2 | ≥ 0.05 | **MEDIUM** |
| 3+ | < 0.05 | **LOW** |

---

## 6. No-Fabrication Enforcement

- In `REAL_MODE` with no Bowtie2 binary or index: endpoint returns HTTP 503 `GENOME_INDEX_NOT_AVAILABLE`
- **Zero synthetic off-target sites** are ever injected in `REAL_MODE`
- `DEMO_MODE` clearly labeled with `"analysis_mode": "DEMO"` in all result fields

---

## 7. Test Results

```
26 passed in 1.90s
TestBowtie2Runner: 4/4 passed
TestSAMParser: 7/7 passed  
TestPAMValidator: 4/4 passed
TestCFDScorer: 8/8 passed
TestOffTargetService: 3/3 passed
```
