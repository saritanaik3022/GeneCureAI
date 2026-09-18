"""
Comprehensive Scientific Validation Script for Stage 4 (GRCh38 Off-Target Analysis & CFD)
and Stage 5 (TOPSIS Multi-Criteria Ranking) across 9 benchmark cancer genes.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import time
from backend.app.services.pipeline_orchestrator import pipeline_orchestrator

BENCHMARK_GENES = [
    # Cancer Type, Gene Symbol
    ("Breast", "BRCA1"),
    ("Breast", "HER2"),
    ("Breast", "TP53"),
    ("Lung", "EGFR"),
    ("Lung", "KRAS"),
    ("Lung", "ALK"),
    ("Liver", "CTNNB1"),
    ("Liver", "AXIN1"),
    ("Liver", "TERT")
]

def run_9_gene_validation():
    print("=" * 80)
    print("STARTING SCIENTIFIC VALIDATION: STAGE 4 (GRCh38 CFD) & STAGE 5 (TOPSIS)")
    print("=" * 80)

    results_summary = []
    output_dir = Path("data/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "stage4_stage5_validation_results.json"

    for cancer_type, gene in BENCHMARK_GENES:
        print(f"\n---> Executing Pipeline for {gene} ({cancer_type} Cancer)...")
        t0 = time.time()
        res = pipeline_orchestrator.execute_pipeline(
            cancer_type=cancer_type,
            gene_symbol=gene,
            top_n=5
        )
        elapsed = round(time.time() - t0, 2)
        status = res.get("status")
        total_scanned = res.get("total_guides_scanned", 0)
        ranked = res.get("ranked_guides", [])

        print(f"     Status: {status} in {elapsed}s | Total Scanned: {total_scanned} | Ranked: {len(ranked)}")

        # Extract Stage 4 off-target and Stage 5 details
        off_target_summary = next((s for s in res.get("stage_summaries", []) if s.get("stage_number") == 4), {})
        topsis_summary = next((s for s in res.get("stage_summaries", []) if s.get("stage_number") == 5), {})

        top_guides = []
        for g in ranked[:3]:
            top_guides.append({
                "rank": g["rank"],
                "protospacer": g["protospacer_sequence"],
                "pam": g["pam"],
                "chromosome": g.get("chromosome"),
                "genomic_start": g.get("genomic_start"),
                "genomic_end": g.get("genomic_end"),
                "gc_content": g["gc_content"],
                "on_target_score": g["on_target_criterion"],
                "off_target_safety": g["off_target_criterion"],
                "cancer_relevance": g["cancer_relevance_criterion"],
                "gc_optimality": g["gc_optimality_criterion"],
                "closeness_score": g["closeness_score"],
                "d_plus": g["distance_positive_ideal"],
                "d_minus": g["distance_negative_ideal"],
            })

        gene_record = {
            "gene_symbol": gene,
            "cancer_type": cancer_type,
            "status": status,
            "elapsed_seconds": elapsed,
            "total_guides_scanned": total_scanned,
            "total_ranked": len(ranked),
            "stage_4_summary": off_target_summary.get("summary", ""),
            "stage_5_summary": topsis_summary.get("summary", ""),
            "top_3_guides": top_guides
        }
        results_summary.append(gene_record)

        if top_guides:
            print(f"     Top Guide #1: {top_guides[0]['protospacer']} (PAM: {top_guides[0]['pam']})")
            print(f"     Criteria: OnTarget={top_guides[0]['on_target_score']}, OffTargetSafety={top_guides[0]['off_target_safety']}, CancerRel={top_guides[0]['cancer_relevance']}, GCOpt={top_guides[0]['gc_optimality']}")
            print(f"     TOPSIS Closeness: {top_guides[0]['closeness_score']} (D+: {top_guides[0]['d_plus']}, D-: {top_guides[0]['d_minus']})")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)

    print("\n" + "=" * 80)
    print(f"VALIDATION COMPLETE! Results written to {out_file}")
    print("=" * 80)

if __name__ == "__main__":
    run_9_gene_validation()
