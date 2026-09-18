# Feature Specification: `gene-cure-v1-105`

## Executive Summary
This document provides the formal scientific specification of the **exact 105 engineered biophysical and positional features** used in the GeneCureAI on-target CRISPR activity pipeline.

- **Feature Version Identifier**: `gene-cure-v1-105`
- **Total Feature Count**: Exactly 105 features
- **Input Domain**: 30-nucleotide genomic context (4-nt 5' flank + 20-nt guide sequence + 3-nt NGG PAM + 3-nt 3' flank)
- **Zero-Placeholder Guarantee**: 100% of all 105 features are dynamically computed using verified biophysical, thermodynamic, and positional algorithms with zero placeholder values.

---

## Breakdown by Feature Category

| Category | Index Range | Count | Primary Methodology |
| :--- | :--- | :--- | :--- |
| **Single Nucleotide Positional** | 0 – 27 | 28 | Doench 2016 single-mer position-specific preferences at 7 critical coordinates |
| **Dinucleotide Positional Interaction** | 28 – 83 | 56 | 14 structural adjacent pairs across guide & PAM evaluating purine/pyrimidine/GC/AT stacking |
| **GC Content Metrics** | 84 – 91 | 8 | Regional GC content (guide, seed, distal, 30-mer, deviation from 50%, flanks, seed/distal ratio) |
| **Thermodynamics & Stacking Free Energy** | 92 – 99 | 8 | Wallace melting temperatures ($T_m$) & SantaLucia 1998 Nearest-Neighbor $\Delta G^\circ_{37}$ stacking parameters |
| **Sequence Complexity & Motifs** | 100 – 104 | 5 | Pol III terminator (`TTTT`), G-quadruplex risk (`GGGG`), homopolymers, PAM-proximal `GG` |
| **Total** | **0 – 104** | **105** | **Fixed-Length Feature Vector** |

---

## Detailed Specification Table (All 105 Features)

| Index | Feature Name | Category | Mathematical Formulation | Expected Range |
| :--- | :--- | :--- | :--- | :--- |
| **0** | `single_flank5_p3_A` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[3] == \text{'A' else } 0.0$ | [0.0, 1.0] |
| **1** | `single_flank5_p3_C` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[3] == \text{'C' else } 0.0$ | [0.0, 1.0] |
| **2** | `single_flank5_p3_G` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[3] == \text{'G' else } 0.0$ | [0.0, 1.0] |
| **3** | `single_flank5_p3_T` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[3] == \text{'T' else } 0.0$ | [0.0, 1.0] |
| **4** | `single_guide_p1_A` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[4] == \text{'A' else } 0.0$ | [0.0, 1.0] |
| **5** | `single_guide_p1_C` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[4] == \text{'C' else } 0.0$ | [0.0, 1.0] |
| **6** | `single_guide_p1_G` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[4] == \text{'G' else } 0.0$ | [0.0, 1.0] |
| **7** | `single_guide_p1_T` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[4] == \text{'T' else } 0.0$ | [0.0, 1.0] |
| **8** | `single_guide_p2_A` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[5] == \text{'A' else } 0.0$ | [0.0, 1.0] |
| **9** | `single_guide_p2_C` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[5] == \text{'C' else } 0.0$ | [0.0, 1.0] |
| **10** | `single_guide_p2_G` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[5] == \text{'G' else } 0.0$ | [0.0, 1.0] |
| **11** | `single_guide_p2_T` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[5] == \text{'T' else } 0.0$ | [0.0, 1.0] |
| **12** | `single_guide_p16_A` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[19] == \text{'A' else } 0.0$ | [0.0, 1.0] |
| **13** | `single_guide_p16_C` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[19] == \text{'C' else } 0.0$ | [0.0, 1.0] |
| **14** | `single_guide_p16_G` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[19] == \text{'G' else } 0.0$ | [0.0, 1.0] |
| **15** | `single_guide_p16_T` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[19] == \text{'T' else } 0.0$ | [0.0, 1.0] |
| **16** | `single_guide_p18_A` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[21] == \text{'A' else } 0.0$ | [0.0, 1.0] |
| **17** | `single_guide_p18_C` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[21] == \text{'C' else } 0.0$ | [0.0, 1.0] |
| **18** | `single_guide_p18_G` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[21] == \text{'G' else } 0.0$ | [0.0, 1.0] |
| **19** | `single_guide_p18_T` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[21] == \text{'T' else } 0.0$ | [0.0, 1.0] |
| **20** | `single_guide_p19_A` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[22] == \text{'A' else } 0.0$ | [0.0, 1.0] |
| **21** | `single_guide_p19_C` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[22] == \text{'C' else } 0.0$ | [0.0, 1.0] |
| **22** | `single_guide_p19_G` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[22] == \text{'G' else } 0.0$ | [0.0, 1.0] |
| **23** | `single_guide_p19_T` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[22] == \text{'T' else } 0.0$ | [0.0, 1.0] |
| **24** | `single_guide_p20_A` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[23] == \text{'A' else } 0.0$ | [0.0, 1.0] |
| **25** | `single_guide_p20_C` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[23] == \text{'C' else } 0.0$ | [0.0, 1.0] |
| **26** | `single_guide_p20_G` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[23] == \text{'G' else } 0.0$ | [0.0, 1.0] |
| **27** | `single_guide_p20_T` | Single Nucleotide Positional | $1.0\text{ if } \text{seq}[23] == \text{'T' else } 0.0$ | [0.0, 1.0] |
| **28–83** | `dimer_pair_{i}_{j}_{metric}` (56 features) | Dinucleotide Positional Interaction | Evaluates 14 structural pairs with 4 metrics each: Purine-Purine, Pyrimidine-Pyrimidine, Strong GC, Weak AT | [0.0, 1.0] |
| **84** | `gc_guide` | GC Content Metrics | Count of (G+C) in 20-nt guide / 20.0 | [0.0, 1.0] |
| **85** | `gc_seed` | GC Content Metrics | Count of (G+C) in 10-nt seed (pos 14..23) / 10.0 | [0.0, 1.0] |
| **86** | `gc_distal` | GC Content Metrics | Count of (G+C) in 10-nt distal (pos 4..13) / 10.0 | [0.0, 1.0] |
| **87** | `gc_full_30mer` | GC Content Metrics | Count of (G+C) in 30-nt context / 30.0 | [0.0, 1.0] |
| **88** | `gc_deviation_optimal` | GC Content Metrics | $| \text{gc\_guide} - 0.50 |$ | [0.0, 0.5] |
| **89** | `gc_5prime_flank` | GC Content Metrics | Count of (G+C) in 4-nt 5' flank / 4.0 | [0.0, 1.0] |
| **90** | `gc_3prime_flank` | GC Content Metrics | Count of (G+C) in 3-nt 3' flank / 3.0 | [0.0, 1.0] |
| **91** | `gc_seed_distal_ratio` | GC Content Metrics | $\text{gc\_seed} / (\text{gc\_distal} + 0.05)$ | [0.0, 20.0] |
| **92** | `tm_guide_wallace` | Thermodynamics | $2 \times (\text{A}+\text{T}) + 4 \times (\text{G}+\text{C})$ for 20-nt guide | [40.0, 80.0] |
| **93** | `tm_seed_wallace` | Thermodynamics | $2 \times (\text{A}+\text{T}) + 4 \times (\text{G}+\text{C})$ for 10-nt seed | [20.0, 40.0] |
| **94** | `tm_distal_wallace` | Thermodynamics | $2 \times (\text{A}+\text{T}) + 4 \times (\text{G}+\text{C})$ for 10-nt distal | [20.0, 40.0] |
| **95** | `tm_full_wallace` | Thermodynamics | $2 \times (\text{A}+\text{T}) + 4 \times (\text{G}+\text{C})$ for 30-nt context | [60.0, 120.0] |
| **96** | `delta_g_seed_nn` | Thermodynamics | SantaLucia (1998) Nearest-Neighbor $\sum \Delta G^\circ_{37}$ (kcal/mol) for 10-nt seed | [-30.0, 0.0] |
| **97** | `delta_g_distal_nn` | Thermodynamics | SantaLucia (1998) Nearest-Neighbor $\sum \Delta G^\circ_{37}$ (kcal/mol) for 10-nt distal | [-30.0, 0.0] |
| **98** | `delta_g_guide_nn` | Thermodynamics | SantaLucia (1998) Nearest-Neighbor $\sum \Delta G^\circ_{37}$ (kcal/mol) for 20-nt guide | [-60.0, 0.0] |
| **99** | `thermo_asymmetry` | Thermodynamics | $\Delta G^\circ_{\text{seed}} - \Delta G^\circ_{\text{distal}}$ (Internal R-loop energy gradient) | [-30.0, 30.0] |
| **100** | `has_poly_t` | Sequence Complexity & Motifs | $1.0\text{ if 'TTTT' in sequence else } 0.0$ (Pol III Terminator) | [0.0, 1.0] |
| **101** | `has_poly_g` | Sequence Complexity & Motifs | $1.0\text{ if 'GGGG' in sequence else } 0.0$ (G-quadruplex Risk) | [0.0, 1.0] |
| **102** | `has_poly_c` | Sequence Complexity & Motifs | $1.0\text{ if 'CCCC' in sequence else } 0.0$ (Poly-C Tract) | [0.0, 1.0] |
| **103** | `has_poly_a` | Sequence Complexity & Motifs | $1.0\text{ if 'AAAA' in sequence else } 0.0$ (Poly-A Tract) | [0.0, 1.0] |
| **104** | `has_pam_proximal_gg` | Sequence Complexity & Motifs | $1.0\text{ if 'GG' in guide}[18:20]\text{ else } 0.0$ (Cleavage Motif) | [0.0, 1.0] |
