# Master Scientific Data Provenance & Methodology Audit

**Audit Date**: 2026-08-15  
**Project**: Gene-Cure AI  
**Scope**: Verification of genomic references, training datasets, feature representations, off-target alignment indices, and scoring matrices.

---

## 1. Reference Genome & Annotation

| Resource | Source / Version | File Path / Identifier | Classification | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **Reference Genome** | GRCh38.p14 Primary Assembly | `C:\Users\GeneCureAI\data\genome\GRCh38.primary_assembly.genome.fa` | SOURCE-DERIVED | Verified (Indexed via `FASTAReader` / `.fai`) |
| **Gene Annotation** | GENCODE v46 Comprehensive | `C:\Users\GeneCureAI\data\annotation\gencode.v46.annotation.gtf` | SOURCE-DERIVED | Verified (58,381 gene records parsed) |
| **Bowtie2 Genome Index** | GRCh38 Pre-built Index | `C:\Users\GeneCureAI\data\bowtie2_index\GRCh38.*.bt2` | SOURCE-DERIVED | Verified (6 standard `.bt2` index files present) |

---

## 2. On-Target Training Dataset & Target Label

| Item | Value / Description | Source / Provenance | Classification |
| :--- | :--- | :--- | :--- |
| **Dataset Source** | `C:\Users\GeneCureAI\data\doench2016\doench2016_ruleset2_train.csv` | Doench et al., *Nat Biotechnol* 34, 184–191 (2016) | SOURCE-DERIVED |
| **Sample Count** | 5,310 Validated 30-mer sgRNA records | Verified from raw CSV inspection | COMPUTED RESULT |
| **Target Variable** | `score_drug_gene_rank` | Doench viability-screen rank-normalized activity score across screens | SOURCE-DERIVED |
| **Scientific Meaning** | Relative on-target knockout/viability score within experimental screening assays (normalized to [0.0, 1.0]). | Empirical phenotypic screen rank metric | SOURCE-DERIVED |

> [!NOTE]
> `score_drug_gene_rank` reflects relative viability/knockout phenotypes observed across cellular drug and gene screens in the Doench 2016 study. It is preserved without modification as the ground truth training target for regression modeling.

---

## 3. Feature Engineering Provenance (105 Features)

- **Feature Version**: `gene-cure-v1-105`
- **Total Feature Count**: Exactly 105 engineered features
- **Classification**: **GENE-CURE ENGINEERED BIOPHYSICAL REPRESENTATION**

### Categorical Attribution:
1. **Single-Nucleotide Positional (28 Features, Indices 0–27)**:
   - *Methodology*: Doench 2016 single-mer coordinate preferences evaluated across 7 functional positions in 30-mer context ($7 \times 4\text{ bases} = 28$).
   - *Classification*: GENE-CURE ENGINEERED (Derived from Doench single-mer positional preferences).
2. **Dinucleotide Positional Interaction (56 Features, Indices 28–83)**:
   - *Methodology*: Evaluates stacking, rigidity, and base pairing strength across 14 adjacent structural pairs ($14 \times 4\text{ biophysical metrics} = 56$).
   - *Classification*: GENE-CURE ENGINEERED.
3. **GC Content Metrics (8 Features, Indices 84–91)**:
   - *Methodology*: Regional GC content (guide, seed, distal, full 30-mer, 50% deviation, 5' flank, 3' flank, seed/distal ratio).
   - *Classification*: GENE-CURE ENGINEERED.
4. **Thermodynamics & Stacking Free Energy (8 Features, Indices 92–99)**:
   - *Methodology*: Wallace melting temperatures ($T_m$) and SantaLucia (PNAS 1998) Unified Nearest-Neighbor $\sum \Delta G^\circ_{37}$ stacking parameters for seed, distal, and full guide regions.
   - *Classification*: ESTABLISHED BIOPHYSICAL CALCULATIONS (SantaLucia 1998 + Wallace).
5. **Sequence Complexity & Motifs (5 Features, Indices 100–104)**:
   - *Methodology*: Pol III transcription terminator (`TTTT`), G-quadruplex risk (`GGGG`), homopolymers (`CCCC`, `AAAA`), and cleavage motif (`GG`).
   - *Classification*: ESTABLISHED BIOLOGICAL MOTIFS.

---

## 4. Off-Target Alignment & CFD Scoring Provenance

| Component | Source / Methodology | Classification | Status |
| :--- | :--- | :--- | :--- |
| **Genome Search** | Bowtie2 short-read aligner against GRCh38 | SOURCE-DERIVED | Implemented / Index Verified |
| **SAM Parser** | 1-based coordinate mapping, CIGAR & MD mismatch extraction | COMPUTED RESULT | Implemented |
| **PAM Validation** | Direct GRCh38 FASTA random access seek via `FASTAReader` | COMPUTED RESULT | Implemented |
| **CFD Matrix** | Doench et al. (Nat Biotechnol 2016) Cutting Frequency Determination matrix | SOURCE-DERIVED | Implemented |
| **Specificity Formula** | $\text{Specificity} = \frac{1}{1 + \sum \text{CFD}} \times 100$ | SOURCE-DERIVED | Implemented |
