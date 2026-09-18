"""
Feature Schema and Definitions for 105-Dimensional CRISPR On-Target Feature Vector.
Deterministic Feature Version: gene-cure-v1-105
"""
from dataclasses import dataclass
from typing import List, Dict, Any

FEATURE_VERSION = "gene-cure-v1-105"
TOTAL_FEATURES = 105


@dataclass(frozen=True)
class FeatureDefinition:
    index: int
    name: str
    category: str
    calculation: str
    input_domain: str
    methodology: str
    dtype: str
    expected_min: float
    expected_max: float


def build_feature_schema() -> List[FeatureDefinition]:
    """
    Constructs the exact 105-feature schema for CRISPR on-target efficiency prediction.
    """
    schema: List[FeatureDefinition] = []
    
    # 1. Single-Nucleotide Features (Indices 0..27, 28 features)
    # 7 key positions across 30-mer context: pos 3 (5' flank -1), pos 4 (guide 1), pos 5 (guide 2),
    # pos 19 (guide 16), pos 21 (guide 18), pos 22 (guide 19), pos 23 (guide 20)
    single_positions = [
        (3, "flank5_p3"),
        (4, "guide_p1"),
        (5, "guide_p2"),
        (19, "guide_p16"),
        (21, "guide_p18"),
        (22, "guide_p19"),
        (23, "guide_p20"),
    ]
    bases = ["A", "C", "G", "T"]
    
    idx = 0
    for pos, pos_name in single_positions:
        for b in bases:
            schema.append(FeatureDefinition(
                index=idx,
                name=f"single_{pos_name}_{b}",
                category="Single Nucleotide Positional",
                calculation=f"1.0 if sequence[{pos}] == '{b}' else 0.0",
                input_domain="30-nt context",
                methodology="Doench 2016 single-mer position-specific preference",
                dtype="float32",
                expected_min=0.0,
                expected_max=1.0
            ))
            idx += 1
            
    # 2. Dimer Positional Features (Indices 28..83, 56 features)
    # 14 adjacent positional pairs across 30-mer
    dimer_pairs = [
        ((2, 3), "pair_2_3"),
        ((3, 4), "pair_3_4"),
        ((4, 5), "pair_4_5"),
        ((5, 6), "pair_5_6"),
        ((9, 10), "pair_9_10"),
        ((13, 14), "pair_13_14"),
        ((17, 18), "pair_17_18"),
        ((18, 19), "pair_18_19"),
        ((19, 20), "pair_19_20"),
        ((20, 21), "pair_20_21"),
        ((21, 22), "pair_21_22"),
        ((22, 23), "pair_22_23"),
        ((23, 24), "pair_23_24"),
        ((26, 27), "pair_26_27"),
    ]
    dimer_metrics = [
        ("purine_purine", "1.0 if dimer in {AA, AG, GA, GG} else 0.0"),
        ("pyrimidine_pyrimidine", "1.0 if dimer in {CC, CT, TC, TT} else 0.0"),
        ("strong_pair", "1.0 if dimer in {GG, GC, CG, CC} else 0.0"),
        ("weak_pair", "1.0 if dimer in {AA, AT, TA, TT} else 0.0"),
    ]
    
    for (p1, p2), pair_name in dimer_pairs:
        for metric_key, calc_desc in dimer_metrics:
            schema.append(FeatureDefinition(
                index=idx,
                name=f"dimer_{pair_name}_{metric_key}",
                category="Dinucleotide Positional Interaction",
                calculation=calc_desc,
                input_domain="30-nt context adjacent pairs",
                methodology="Doench 2016 dinucleotide stacking and flexibility proxy",
                dtype="float32",
                expected_min=0.0,
                expected_max=1.0
            ))
            idx += 1
            
    # 3. GC Content Metrics (Indices 84..91, 8 features)
    gc_defs = [
        ("gc_guide", "GC count in 20-nt guide / 20.0", 0.0, 1.0),
        ("gc_seed", "GC count in 10-nt seed (pos 14..23) / 10.0", 0.0, 1.0),
        ("gc_distal", "GC count in 10-nt distal (pos 4..13) / 10.0", 0.0, 1.0),
        ("gc_full_30mer", "GC count in full 30-mer context / 30.0", 0.0, 1.0),
        ("gc_deviation_optimal", "abs(gc_guide - 0.50)", 0.0, 0.5),
        ("gc_5prime_flank", "GC count in 4-nt 5' flank / 4.0", 0.0, 1.0),
        ("gc_3prime_flank", "GC count in 3-nt 3' flank / 3.0", 0.0, 1.0),
        ("gc_seed_distal_ratio", "gc_seed / (gc_distal + 0.05)", 0.0, 20.0),
    ]
    for name, calc_desc, min_val, max_val in gc_defs:
        schema.append(FeatureDefinition(
            index=idx,
            name=name,
            category="GC Content Metrics",
            calculation=calc_desc,
            input_domain="30-nt context subregions",
            methodology="Regional GC content and optimal composition balance",
            dtype="float32",
            expected_min=min_val,
            expected_max=max_val
        ))
        idx += 1
        
    # 4. Thermodynamic & Nearest-Neighbor Stacking Features (Indices 92..99, 8 features)
    thermo_defs = [
        ("tm_guide_wallace", "Wallace Tm: 2*(A+T) + 4*(G+C) for 20-nt guide", 40.0, 80.0),
        ("tm_seed_wallace", "Wallace Tm: 2*(A+T) + 4*(G+C) for 10-nt seed", 20.0, 40.0),
        ("tm_distal_wallace", "Wallace Tm: 2*(A+T) + 4*(G+C) for 10-nt distal", 20.0, 40.0),
        ("tm_full_wallace", "Wallace Tm: 2*(A+T) + 4*(G+C) for 30-nt context", 60.0, 120.0),
        ("delta_g_seed_nn", "SantaLucia 1998 nearest-neighbor stacking deltaG (kcal/mol) for seed", -30.0, 0.0),
        ("delta_g_distal_nn", "SantaLucia 1998 nearest-neighbor stacking deltaG (kcal/mol) for distal", -30.0, 0.0),
        ("delta_g_guide_nn", "SantaLucia 1998 nearest-neighbor stacking deltaG (kcal/mol) for full guide", -60.0, 0.0),
        ("thermo_asymmetry", "delta_g_seed_nn - delta_g_distal_nn (R-loop gradient)", -30.0, 30.0),
    ]
    for name, calc_desc, min_val, max_val in thermo_defs:
        schema.append(FeatureDefinition(
            index=idx,
            name=name,
            category="Thermodynamics & Stacking Free Energy",
            calculation=calc_desc,
            input_domain="30-nt context subregions",
            methodology="SantaLucia 1998 NN thermodynamic parameters & Wallace Tm",
            dtype="float32",
            expected_min=min_val,
            expected_max=max_val
        ))
        idx += 1
        
    # 5. Sequence Complexity & Motif Flags (Indices 100..104, 5 features)
    motif_defs = [
        ("has_poly_t", "1.0 if 'TTTT' in sequence else 0.0 (Pol III terminator)", 0.0, 1.0),
        ("has_poly_g", "1.0 if 'GGGG' in sequence else 0.0 (G-quadruplex risk)", 0.0, 1.0),
        ("has_poly_c", "1.0 if 'CCCC' in sequence else 0.0 (Poly-C tract)", 0.0, 1.0),
        ("has_poly_a", "1.0 if 'AAAA' in sequence else 0.0 (Poly-A tract)", 0.0, 1.0),
        ("has_pam_proximal_gg", "1.0 if 'GG' in guide[18:20] else 0.0 (Cleavage motif)", 0.0, 1.0),
    ]
    for name, calc_desc, min_val, max_val in motif_defs:
        schema.append(FeatureDefinition(
            index=idx,
            name=name,
            category="Sequence Complexity & Motifs",
            calculation=calc_desc,
            input_domain="30-nt context",
            methodology="Biological sequence structural motifs and termination signals",
            dtype="float32",
            expected_min=min_val,
            expected_max=max_val
        ))
        idx += 1
        
    assert len(schema) == TOTAL_FEATURES, f"Expected {TOTAL_FEATURES} features, got {len(schema)}"
    return schema


FEATURE_SCHEMA = build_feature_schema()
FEATURE_NAMES: List[str] = [f.name for f in FEATURE_SCHEMA]
FEATURE_CATEGORIES: Dict[str, List[int]] = {}
for feat in FEATURE_SCHEMA:
    FEATURE_CATEGORIES.setdefault(feat.category, []).append(feat.index)
