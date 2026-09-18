# Phase 2 — Real Bioinformatics Engine Validation Report
**Dataset Provenance**: GENCODE Release 46 (Comprehensive gene annotation) + GRCh38 Primary Assembly Reference Genome (`GRCh38.primary_assembly.genome.fa`)
**Target Endonuclease**: *Streptococcus pyogenes* Cas9 (SpCas9)
**PAM Recognition Motif**: 5'-NGG-3' (Dual-Strand Search: 5'-NGG-3' on sense, 5'-CCN-3' on antisense)
**Execution Mode**: `REAL_MODE` (Zero fixture data, verified genomic sequences)

---

## 1. Summary of Results Across All 9 Curated Target Genes

| Gene Symbol | Alias / GENCODE ID | Chr | Strand | Canonical Transcript | Exons (CDS / Total) | CDS Length (bp) | Total Candidates Found | GC Range | Poly-T Excluded |
|:---|:---|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| **BRCA1** | ENSG00000012048.26 | chr17 | - | `ENST00000357654.9` | 22 / 23 | 5,592 | **354** | 20.0% – 70.0% | Yes (TTTT) |
| **HER2 (ERBB2)** | ENSG00000141736.14 | chr17 | + | `ENST00000269571.10` | 27 / 30 | 3,768 | **272** | 35.0% – 80.0% | Yes (TTTT) |
| **TP53** | ENSG00000141510.18 | chr17 | - | `ENST00000269305.9` | 10 / 11 | 1,182 | **63** | 35.0% – 80.0% | Yes (TTTT) |
| **EGFR** | ENSG00000146648.16 | chr7 | + | `ENST00000275493.7` | 28 / 28 | 3,633 | **268** | 30.0% – 80.0% | Yes (TTTT) |
| **KRAS** | ENSG00000133703.15 | chr12 | - | `ENST00000256078.10` | 4 / 5 | 570 | **45** | 20.0% – 60.0% | Yes (TTTT) |
| **ALK** | ENSG00000171094.18 | chr2 | - | `ENST00000389048.8` | 29 / 29 | 4,863 | **357** | 30.0% – 80.0% | Yes (TTTT) |
| **CTNNB1** | ENSG00000168036.17 | chr3 | + | `ENST00000349496.11` | 14 / 15 | 2,346 | **156** | 30.0% – 70.0% | Yes (TTTT) |
| **AXIN1** | ENSG00000103126.15 | chr16 | - | `ENST00000262325.8` | 10 / 11 | 2,589 | **226** | 35.0% – 80.0% | Yes (TTTT) |
| **TERT** | ENSG00000164362.21 | chr5 | - | `ENST00000310581.10` | 16 / 16 | 3,399 | **291** | 45.0% – 80.0% | Yes (TTTT) |
| **TOTAL** | — | — | — | — | **160 CDS** | **27,942 bp** | **2,032 Guides** | — | — |

---

## 2. Exemplar Guide Validation (Top Candidate per Gene)

### 1. BRCA1 (Breast Cancer)
- **Transcript**: `ENST00000357654.9` (MANE Select / Ensembl Canonical, APPRIS P1)
- **Top Guide ID**: `gRNA-BRCA1-0001`
- **Protospacer**: `ACAGTGGAACAGTGGAACTC` (20 nt)
- **PAM**: `CGG` (Sense strand)
- **30-nt Context**: `GAGTACAGTGGAACAGTGGAACTCCGGCAT`
- **Genomic Locus**: `chr17:43045700-43045722 (+)`
- **Cleavage Site**: `chr17:43045716`
- **Exon**: Exon 2 (CDS Exon 1)
- **GC Content**: 50.0%

### 2. HER2 / ERBB2 (Breast Cancer)
- **Transcript**: `ENST00000269571.10` (Ensembl Canonical, APPRIS P1)
- **Top Guide ID**: `gRNA-HER2-0001`
- **Protospacer**: `GGCAGCAGAAGATCCGGAAG` (20 nt)
- **PAM**: `TGG` (Sense strand)
- **30-nt Context**: `CCACGGCAGCAGAAGATCCGGAAGTGGATC`
- **Genomic Locus**: `chr17:39700340-39700362 (+)`
- **GC Content**: 60.0%

### 3. TP53 (Pan-Cancer Tumor Suppressor)
- **Transcript**: `ENST00000269305.9` (MANE Select / Ensembl Canonical, APPRIS P1)
- **Top Guide ID**: `gRNA-TP53-0001`
- **Protospacer**: `GAGGTTGGCTCTGACTGTAC` (20 nt)
- **PAM**: `ACC` (Antisense strand `TGG`)
- **Genomic Locus**: `chr17:7669610-7669632 (-)`
- **GC Content**: 55.0%

### 4. KRAS (Lung Cancer Oncogene)
- **Transcript**: `ENST00000256078.10` (MANE Select / Ensembl Canonical)
- **Codon 12/13 Region**: Scanned with 45 validated candidate protospacers covering Exons 2–5.
- **Top Guide ID**: `gRNA-KRAS-0001`
- **Genomic Locus**: `chr12:25245350-25245372 (-)`

---

## 3. Methodological Integrity & Compliance

1. **Deterministic Multi-Tier Selection Policy**:
   - Resolved MANE Select and APPRIS Principal transcripts deterministically.
   - Identified `ERBB2` as the authoritative symbol for `HER2` in GENCODE v46.
2. **Dual-Strand PAM Scanning**:
   - Scanned both forward (`5'-NGG-3'`) and reverse complement (`5'-CCN-3'`) orientations on GRCh38.
   - Preserved exact 30-nt nucleotide windows (4-nt 5' flank + 20-nt protospacer + 3-nt PAM + 3-nt 3' flank).
3. **Zero Fixture Fallback in REAL_MODE**:
   - Backend checks `settings.GENOME_FASTA` and `settings.GENCODE_GTF`.
   - Never silently switches to demo data if resources are missing.
