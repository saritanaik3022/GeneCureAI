import sys, os
sys.path.insert(0, os.path.abspath("."))
import time, re
from pathlib import Path
from bioinformatics.genome.fasta_reader import FASTAReader
from bioinformatics.off_target.cfd_scorer import CFDScorer
from bioinformatics.off_target.pam_validator import PAMValidator
from bioinformatics.off_target.models import OffTargetSite, GuideOffTargetSummary
from backend.app.services.bioinformatics_service import BioinformaticsService
from backend.app.services.topsis_service import topsis_service

print("--- Step 1: Candidate Generation ---")
bio_svc = BioinformaticsService.get_instance()
scan_res = bio_svc.candidate_generator.scan_gene_exons("BRCA1")
candidates = scan_res.candidates[:5]
guide_seqs = [c.protospacer_sequence for c in candidates]
print(f"Scanned {len(scan_res.candidates)} BRCA1 guides. Testing top 5:")
for i, c in enumerate(candidates):
    print(f"  Guide {i+1}: {c.protospacer_sequence} PAM={c.pam_sequence} pos={c.chromosome}:{c.genomic_start} strand={c.strand}")

fasta_reader = FASTAReader(Path("C:/Users/GeneCureAI/data/genome/GRCh38.primary_assembly.genome.fa"))
pam_val = PAMValidator(fasta_reader=fasta_reader)

def direct_grch38_search(guide_sequences, chromosomes=None, max_mismatches=3):
    seed_len = 10
    guide_info = []
    for i, g in enumerate(guide_sequences):
        g_clean = g.strip().upper()
        seed = g_clean[-seed_len:]
        seed_rc = FASTAReader.reverse_complement(seed)
        guide_info.append({
            "idx": i,
            "qname": f"guide_{i+1}",
            "guide": g_clean,
            "seed": seed,
            "seed_rc": seed_rc
        })
    
    fwd_seeds = {info["seed"]: info for info in guide_info}
    rev_seeds = {info["seed_rc"]: info for info in guide_info}
    
    fwd_regex = re.compile(r'(' + '|'.join(re.escape(s) for s in fwd_seeds.keys()) + r')([ACGT][GA]G)')
    rev_regex = re.compile(r'(C[CT][ACGT])(' + '|'.join(re.escape(s) for s in rev_seeds.keys()) + r')')
    
    target_chroms = chromosomes or ["chr17"]
    records = []
    chunk_size = 10000000
    
    for chrom in target_chroms:
        chrom_len = len(fasta_reader._pyfaidx_fasta[chrom])
        for start in range(1, chrom_len, chunk_size):
            end = min(start + chunk_size + 100, chrom_len)
            chunk = fasta_reader.get_sequence(chrom, start, end)
            
            for m in fwd_regex.finditer(chunk):
                seed_matched = m.group(1)
                info = fwd_seeds.get(seed_matched)
                if not info: continue
                idx_in_chunk = m.start()
                t_start = idx_in_chunk - (20 - seed_len)
                if t_start >= 0 and t_start + 23 <= len(chunk):
                    t_seq = chunk[t_start : t_start + 20]
                    pam = chunk[t_start + 20 : t_start + 23]
                    pos = start + t_start
                    if PAMValidator.is_valid_spcas9_pam(pam):
                        g_seq = info["guide"]
                        mm_pos = [k + 1 for k in range(20) if g_seq[k] != t_seq[k]]
                        if len(mm_pos) <= max_mismatches:
                            records.append({
                                "query_name": info["qname"],
                                "chromosome": chrom, "position": pos, "strand": "+",
                                "mismatch_count": len(mm_pos), "mismatch_positions": mm_pos,
                                "aligned_sequence": t_seq, "pam": pam, "cigar": "20M"
                            })
                            
            for m in rev_regex.finditer(chunk):
                seed_rc_matched = m.group(2)
                info = rev_seeds.get(seed_rc_matched)
                if not info: continue
                idx_in_chunk = m.start()
                t_start = idx_in_chunk + 3
                if t_start + 20 <= len(chunk):
                    raw_t = chunk[t_start : t_start + 20]
                    raw_pam = chunk[idx_in_chunk : idx_in_chunk + 3]
                    t_seq = FASTAReader.reverse_complement(raw_t)
                    pam = FASTAReader.reverse_complement(raw_pam)
                    pos = start + t_start
                    if PAMValidator.is_valid_spcas9_pam(pam):
                        g_seq = info["guide"]
                        mm_pos = [k + 1 for k in range(20) if g_seq[k] != t_seq[k]]
                        if len(mm_pos) <= max_mismatches:
                            records.append({
                                "query_name": info["qname"],
                                "chromosome": chrom, "position": pos, "strand": "-",
                                "mismatch_count": len(mm_pos), "mismatch_positions": mm_pos,
                                "aligned_sequence": t_seq, "pam": pam, "cigar": "20M"
                            })
    return records

t0 = time.time()
print("\n--- Step 2: Executing Real GRCh38 Genome Search ---")
parsed_records = direct_grch38_search(guide_seqs, ["chr17"], max_mismatches=3)
print(f"Genome alignment search on GRCh38 completed in {round(time.time()-t0, 3)}s.")
print(f"Total alignment records found: {len(parsed_records)}")

# Group by guide
grouped = {}
for r in parsed_records:
    grouped.setdefault(r["query_name"], []).append(r)

summaries = []
for i, guide in enumerate(guide_seqs):
    qname = f"guide_{i+1}"
    recs = grouped.get(qname, [])
    cand = candidates[i]
    
    sites = []
    cfd_scores = []
    mm_counts = {"0_mismatch": 0, "1_mismatch": 0, "2_mismatch": 0, "3_mismatch": 0}
    
    for r in recs:
        mm = r["mismatch_count"]
        pos = r["position"]
        strand = r["strand"]
        
        # Determine if this alignment is the on-target locus
        is_on_target = (mm == 0 and abs(pos - cand.genomic_start) <= 5 and strand == cand.strand)
        
        if mm == 0: mm_counts["0_mismatch"] += 1
        elif mm == 1: mm_counts["1_mismatch"] += 1
        elif mm == 2: mm_counts["2_mismatch"] += 1
        elif mm >= 3: mm_counts["3_mismatch"] += 1
        
        cfd = CFDScorer.calculate_cfd_score(guide, r["aligned_sequence"], r["pam"], r["mismatch_positions"])
        risk = CFDScorer.determine_risk_level(mm, cfd)
        
        # If it is not the primary on-target site, it counts as an off-target site
        if not is_on_target:
            cfd_scores.append(cfd)
            sites.append(OffTargetSite(
                chromosome=r["chromosome"],
                position=pos,
                strand=strand,
                aligned_sequence=r["aligned_sequence"],
                pam=r["pam"],
                mismatches=mm,
                mismatch_positions=r["mismatch_positions"],
                cigar=r["cigar"],
                cfd_score=cfd,
                annotation="Genomic Off-Target",
                risk_level=risk
            ))
            
    cum_cfd, spec, norm_safety = CFDScorer.calculate_specificity_score(cfd_scores)
    summary = GuideOffTargetSummary(
        guide_sequence=guide,
        total_off_targets=len(sites),
        mismatch_counts=mm_counts,
        cumulative_cfd_score=cum_cfd,
        specificity_score=spec,
        normalized_safety_score=norm_safety,
        sites=sites,
        analysis_mode="REAL",
        search_tool="grch38_direct",
        reference_assembly="GRCh38.p14",
        index_version="GRCh38"
    )
    summaries.append(summary.to_dict())

print("\n--- Step 3: Stage 4 Results ---")
for s in summaries:
    print(f"Guide: {s['guide_sequence']} | Off-targets: {s['total_off_targets']} | Cum CFD: {s['cumulative_cfd_score']:.4f} | Specificity: {s['specificity_score']:.2f}% | Safety: {s['normalized_safety_score']:.4f}")

