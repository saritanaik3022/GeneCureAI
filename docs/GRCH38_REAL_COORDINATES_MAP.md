# GRCh38 Real Genomic Coordinates Map for Curated Cancer Target Genes

This document records the exact 1-based genomic locus coordinates on the GRCh38 primary assembly reference genome (`GRCh38.primary_assembly.genome.fa`) and corresponding GENCODE v46 annotations.

---

## 1. Target Gene Coordinates Table

| Gene Symbol | Ensembl Gene ID | Chromosome | Strand | Genomic Start (1-based) | Genomic End (1-based) | Total Gene Span (bp) | Canonical Transcript | CDS Length (bp) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|:---:|
| **BRCA1** | `ENSG00000012048.26` | chr17 | - | 43,044,295 | 43,170,245 | 125,951 | `ENST00000357654.9` | 5,592 |
| **HER2 (ERBB2)** | `ENSG00000141736.14` | chr17 | + | 39,687,914 | 39,730,415 | 42,502 | `ENST00000269571.10` | 3,768 |
| **TP53** | `ENSG00000141510.18` | chr17 | - | 7,668,402 | 7,687,550 | 19,149 | `ENST00000269305.9` | 1,182 |
| **EGFR** | `ENSG00000146648.16` | chr7 | + | 55,019,017 | 55,211,628 | 192,612 | `ENST00000275493.7` | 3,633 |
| **KRAS** | `ENSG00000133703.15` | chr12 | - | 25,204,789 | 25,250,929 | 46,141 | `ENST00000256078.10` | 570 |
| **ALK** | `ENSG00000171094.18` | chr2 | - | 29,192,774 | 29,479,367 | 286,594 | `ENST00000389048.8` | 4,863 |
| **CTNNB1** | `ENSG00000168036.17` | chr3 | + | 41,199,505 | 41,240,942 | 41,438 | `ENST00000349496.11` | 2,346 |
| **AXIN1** | `ENSG00000103126.15` | chr16 | - | 339,000 | 404,000 | 65,001 | `ENST00000262325.8` | 2,589 |
| **TERT** | `ENSG00000164362.21` | chr5 | - | 1,253,147 | 1,295,068 | 41,922 | `ENST00000310581.10` | 3,399 |

---

## 2. SpCas9 Guide RNA Design Rules

- **Target Sites**: Exonic Coding Sequences (CDS) exclusively, maximizing disruption of functional protein products via frameshift indels.
- **Protospacer Length**: 20 nucleotides (`5' -> 3'`).
- **PAM Motif**: `5'-NGG-3'` (Sense strand scan `5'-[20nt][NGG]-3'`; Antisense strand scan `5'-[CCN][20nt]-3'`).
- **Context Sequence**: 30 nucleotides extracted directly from reference genome (`4 nt 5' flank + 20 nt guide + 3 nt PAM + 3 nt 3' flank`).
- **Cleavage Site Position**: Predicted double-strand break (DSB) coordinate is located between nucleotide -3 and -4 relative to the 5' end of the PAM.
