"""
Stage 5: TOPSIS Multi-Criteria Decision Ranking endpoints.
"""
import numpy as np
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.schemas.topsis import TOPSISRankRequest, TOPSISRankResponse, TOPSISRankedItem
try:
    from backend.app.services.topsis_service import topsis_service
except ImportError:
    from app.services.topsis_service import topsis_service

router = APIRouter()


@router.post("/rank", response_model=TOPSISRankResponse, tags=["Stage 5: TOPSIS Ranking"])
async def rank_guides_with_topsis(request: TOPSISRankRequest):
    """
    Ranks candidate guides using Technique for Order Preference by Similarity
    to Ideal Solution (TOPSIS) across the 4 weighted criteria.
    """
    if not request.candidates:
        return TOPSISRankResponse(
            total_ranked=0,
            weights_applied=request.weights,
            ranked_guides=[]
        )

    # Build decision matrix
    matrix_rows = []
    for cand in request.candidates:
        gc_opt = cand.gc_optimality_score
        if gc_opt is None:
            gc_opt = topsis_service.calculate_gc_optimality(cand.gc_percentage)

        matrix_rows.append([
            cand.on_target_score,
            cand.off_target_safety_score,
            cand.cancer_relevance_score,
            gc_opt
        ])

    decision_matrix = np.array(matrix_rows, dtype=float)
    weights_arr = np.array([
        request.weights.w_on_target,
        request.weights.w_off_target,
        request.weights.w_cancer_relevance,
        request.weights.w_gc_optimality
    ], dtype=float)

    # Run genuine TOPSIS
    topsis_res = topsis_service.run_topsis(decision_matrix, weights=weights_arr)

    ranked_items = []
    for orig_i in np.argsort(-topsis_res["closeness_scores"]):
        cand = request.candidates[orig_i]
        c_score = float(topsis_res["closeness_scores"][orig_i])
        d_pos = float(topsis_res["distance_pos"][orig_i])
        d_neg = float(topsis_res["distance_neg"][orig_i])
        row_vals = decision_matrix[orig_i]
        rank_val = int(topsis_res["ranks"][orig_i])

        ranked_items.append(TOPSISRankedItem(
            rank=rank_val,
            guide_id=cand.guide_id,
            protospacer_sequence=cand.protospacer_sequence,
            pam=cand.pam,
            strand=cand.strand or "+",
            chromosome=cand.chromosome or "",
            genomic_start=cand.genomic_start,
            genomic_end=cand.genomic_end,
            exon_number=cand.exon_number,
            gc_content=cand.gc_percentage,
            closeness_score=round(c_score, 4),
            distance_positive_ideal=round(d_pos, 4),
            distance_negative_ideal=round(d_neg, 4),
            on_target_criterion=round(float(row_vals[0]), 4),
            off_target_criterion=round(float(row_vals[1]), 4),
            cancer_relevance_criterion=round(float(row_vals[2]), 4),
            gc_optimality_criterion=round(float(row_vals[3]), 4),
            context_30nt=cand.context_30nt,
            cleavage_coordinate=cand.cleavage_coordinate
        ))

    # Sort ascending by final rank
    ranked_items.sort(key=lambda x: x.rank)

    return TOPSISRankResponse(
        total_ranked=len(ranked_items),
        weights_applied=request.weights,
        ranked_guides=ranked_items
    )
