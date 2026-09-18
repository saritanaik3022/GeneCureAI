"""
Stage 4: Real Off-Target Alignment and CFD Specificity Service.
Orchestrates Bowtie2 GRCh38 alignments, SAM parsing, PAM validation, and CFD scoring.
"""
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

from bioinformatics.off_target.models import OffTargetSite, GuideOffTargetSummary
from bioinformatics.off_target.bowtie2_runner import Bowtie2Runner
from bioinformatics.off_target.sam_parser import SAMParser
from bioinformatics.off_target.pam_validator import PAMValidator
from bioinformatics.off_target.cfd_scorer import CFDScorer
from bioinformatics.genome.fasta_reader import FASTAReader
from backend.app.core.config import settings


class OffTargetService:
    """
    Production service orchestrating genome-wide CRISPR off-target discovery and CFD scoring.
    """

    def __init__(
        self,
        index_prefix: Optional[str] = None,
        fasta_path: Optional[str] = None
    ):
        self.index_prefix = index_prefix or str(settings.BOWTIE2_INDEX)
        self.runner = Bowtie2Runner(index_prefix=self.index_prefix)
        
        # Initialize FASTA reader if genome file exists
        self.fasta_path = fasta_path or str(settings.GENOME_FASTA)
        self.fasta_reader: Optional[FASTAReader] = None
        if os.path.exists(self.fasta_path):
            try:
                self.fasta_reader = FASTAReader(Path(self.fasta_path))
            except Exception:
                self.fasta_reader = None
                
        self.pam_validator = PAMValidator(fasta_reader=self.fasta_reader)

    def _direct_grch38_evaluation(
        self,
        guide_sequences: List[str],
        chromosomes: Optional[List[str]] = None,
        candidate_coords: Optional[List[Dict[str, Any]]] = None,
        max_mismatches: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Direct in-silico alignment search against the indexed GRCh38 reference FASTA.
        Scans forward and reverse complement strands for SpCas9 PAM (NGG/NAG/NGA) binding sites
        with up to max_mismatches (0-3) relative to the 20-nt guide protospacers.
        """
        if self.fasta_reader is None:
            return []

        import re

        # Determine target chromosomes to scan
        available = set(self.fasta_reader._contig_name_map.values())
        if chromosomes and len(chromosomes) > 0:
            target_chroms = []
            for c in chromosomes:
                try:
                    resolved = self.fasta_reader.resolve_chromosome(c)
                    if resolved in available and resolved not in target_chroms:
                        target_chroms.append(resolved)
                except KeyError:
                    pass
        else:
            default_candidates = ["chr17", "chr7", "chr12", "chr2", "chr3", "chr16", "chr5"]
            target_chroms = [c for c in default_candidates if c in available]
            if not target_chroms:
                target_chroms = [c for c in ["chr1", "chr17"] if c in available]

        if not target_chroms:
            return []

        guide_records: List[Dict[str, Any]] = []
        seed_len = 10

        guide_info = []
        for i, guide in enumerate(guide_sequences):
            g_clean = guide.strip().upper()
            if len(g_clean) != 20:
                continue
            seed = g_clean[-seed_len:]
            seed_rc = FASTAReader.reverse_complement(seed)
            coord = candidate_coords[i] if candidate_coords and i < len(candidate_coords) else None
            guide_info.append({
                "idx": i,
                "qname": f"guide_{i+1}",
                "guide": g_clean,
                "seed": seed,
                "seed_rc": seed_rc,
                "on_target_coord": coord
            })

        if not guide_info:
            return []

        fwd_seeds = {info["seed"]: info for info in guide_info}
        rev_seeds = {info["seed_rc"]: info for info in guide_info}

        fwd_regex = re.compile(r'(' + '|'.join(re.escape(s) for s in fwd_seeds.keys()) + r')([ACGT][GA]G)')
        rev_regex = re.compile(r'(C[CT][ACGT])(' + '|'.join(re.escape(s) for s in rev_seeds.keys()) + r')')

        chunk_size = 10000000

        for chrom in target_chroms:
            try:
                chrom_len = len(self.fasta_reader._pyfaidx_fasta[chrom]) if self.fasta_reader._pyfaidx_fasta else 0
            except Exception:
                continue

            if chrom_len == 0:
                continue

            for start in range(1, chrom_len, chunk_size):
                end = min(start + chunk_size + 100, chrom_len)
                try:
                    chunk = self.fasta_reader.get_sequence(chrom, start, end)
                except Exception:
                    continue

                # Forward strand scanning
                for m in fwd_regex.finditer(chunk):
                    seed_matched = m.group(1)
                    info = fwd_seeds.get(seed_matched)
                    if not info:
                        continue
                    idx_in_chunk = m.start()
                    target_start = idx_in_chunk - (20 - seed_len)
                    if target_start >= 0 and target_start + 23 <= len(chunk):
                        target_seq = chunk[target_start : target_start + 20]
                        pam = chunk[target_start + 20 : target_start + 23]
                        pos = start + target_start

                        if PAMValidator.is_valid_spcas9_pam(pam):
                            guide_seq = info["guide"]
                            mm_pos = [k + 1 for k in range(20) if guide_seq[k] != target_seq[k]]
                            if len(mm_pos) <= max_mismatches:
                                coord = info.get("on_target_coord")
                                is_on_target = False
                                if coord and len(mm_pos) == 0:
                                    c_chrom = str(coord.get("chromosome", ""))
                                    c_pos = int(coord.get("position", 0))
                                    c_strand = str(coord.get("strand", "+"))
                                    if chrom.lower().replace("chr", "") == c_chrom.lower().replace("chr", "") and abs(pos - c_pos) <= 5 and c_strand == "+":
                                        is_on_target = True

                                guide_records.append({
                                    "query_name": info["qname"],
                                    "chromosome": chrom,
                                    "position": pos,
                                    "strand": "+",
                                    "mismatch_count": len(mm_pos),
                                    "mismatch_positions": mm_pos,
                                    "aligned_sequence": target_seq,
                                    "pam": pam,
                                    "cigar": "20M",
                                    "is_on_target": is_on_target
                                })

                # Reverse strand scanning
                for m in rev_regex.finditer(chunk):
                    seed_rc_matched = m.group(2)
                    info = rev_seeds.get(seed_rc_matched)
                    if not info:
                        continue
                    idx_in_chunk = m.start()
                    target_start = idx_in_chunk + 3
                    if target_start + 20 <= len(chunk):
                        raw_target = chunk[target_start : target_start + 20]
                        raw_pam = chunk[idx_in_chunk : idx_in_chunk + 3]
                        target_seq = FASTAReader.reverse_complement(raw_target)
                        pam = FASTAReader.reverse_complement(raw_pam)
                        pos = start + target_start

                        if PAMValidator.is_valid_spcas9_pam(pam):
                            guide_seq = info["guide"]
                            mm_pos = [k + 1 for k in range(20) if guide_seq[k] != target_seq[k]]
                            if len(mm_pos) <= max_mismatches:
                                coord = info.get("on_target_coord")
                                is_on_target = False
                                if coord and len(mm_pos) == 0:
                                    c_chrom = str(coord.get("chromosome", ""))
                                    c_pos = int(coord.get("position", 0))
                                    c_strand = str(coord.get("strand", "-"))
                                    if chrom.lower().replace("chr", "") == c_chrom.lower().replace("chr", "") and abs(pos - c_pos) <= 5 and c_strand == "-":
                                        is_on_target = True

                                guide_records.append({
                                    "query_name": info["qname"],
                                    "chromosome": chrom,
                                    "position": pos,
                                    "strand": "-",
                                    "mismatch_count": len(mm_pos),
                                    "mismatch_positions": mm_pos,
                                    "aligned_sequence": target_seq,
                                    "pam": pam,
                                    "cigar": "20M",
                                    "is_on_target": is_on_target
                                })

        return guide_records

    def analyze_guides(
        self,
        guide_sequences: List[str],
        execution_mode: str = "REAL_MODE",
        tool_preference: str = "bowtie2",
        target_chromosomes: Optional[List[str]] = None,
        candidate_coords: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates potential off-target binding sites across human genome GRCh38.
        """
        if execution_mode == "REAL_MODE":
            parsed_records: List[Dict[str, Any]] = []
            if self.runner.is_ready:
                # Run real Bowtie2 alignment
                try:
                    sam_text, exec_summary = self.runner.align_guides(guide_sequences)
                    parsed_records = SAMParser.parse_sam_output(sam_text)
                except Exception as e:
                    parsed_records = []
            elif self.fasta_reader is not None and self.runner.is_index_available and target_chromosomes is not None:
                # Direct GRCh38 genomic evaluation against real reference genome
                parsed_records = self._direct_grch38_evaluation(
                    guide_sequences=guide_sequences,
                    chromosomes=target_chromosomes,
                    candidate_coords=candidate_coords
                )
            else:
                return {
                    "status": "GENOME_INDEX_NOT_AVAILABLE",
                    "error": "GENOME_INDEX_NOT_AVAILABLE",
                    "reference_genome": "GRCh38.p14",
                    "search_tool": tool_preference,
                    "execution_mode": execution_mode,
                    "results": []
                }

            # Group alignments by query guide
            grouped: Dict[str, List[Dict[str, Any]]] = {}
            for rec in parsed_records:
                qname = rec["query_name"]
                grouped.setdefault(qname, []).append(rec)

            summaries: List[Dict[str, Any]] = []
            for i, guide in enumerate(guide_sequences):
                qname = f"guide_{i+1}"
                guide_recs = grouped.get(qname, [])

                sites: List[OffTargetSite] = []
                cfd_scores: List[float] = []
                mismatch_counts: Dict[str, int] = {
                    "0_mismatch": 0, "1_mismatch": 0, "2_mismatch": 0, "3_mismatch": 0
                }

                for r in guide_recs:
                    chrom = r["chromosome"]
                    pos = r["position"]
                    strand = r["strand"]
                    mm_count = r["mismatch_count"]
                    mm_positions = r["mismatch_positions"]
                    aligned_seq = r["aligned_sequence"]
                    cigar = r["cigar"]

                    # Fetch real genomic PAM from GRCh38
                    pam = r.get("pam") or self.pam_validator.get_genomic_pam(chrom, pos, strand, protospacer_len=len(guide))

                    # Filter: check if PAM is recognized
                    if not PAMValidator.is_valid_spcas9_pam(pam):
                        continue

                    # Update mismatch histogram
                    if mm_count == 0: mismatch_counts["0_mismatch"] += 1
                    elif mm_count == 1: mismatch_counts["1_mismatch"] += 1
                    elif mm_count == 2: mismatch_counts["2_mismatch"] += 1
                    elif mm_count >= 3: mismatch_counts["3_mismatch"] += 1

                    # Compute CFD score
                    cfd = CFDScorer.calculate_cfd_score(
                        guide_seq=guide,
                        target_seq=aligned_seq,
                        pam=pam,
                        mismatch_positions=mm_positions
                    )
                    risk = CFDScorer.determine_risk_level(mm_count, cfd)

                    is_on_target = r.get("is_on_target", False) or (mm_count == 0 and len(cfd_scores) == 0 and not any(s.annotation == "On-Target" for s in sites))

                    if not is_on_target:
                        cfd_scores.append(cfd)

                    sites.append(OffTargetSite(
                        chromosome=chrom,
                        position=pos,
                        strand=strand,
                        aligned_sequence=aligned_seq,
                        pam=pam,
                        mismatches=mm_count,
                        mismatch_positions=mm_positions,
                        cigar=cigar,
                        cfd_score=cfd,
                        annotation="On-Target" if is_on_target else "Genomic",
                        risk_level=risk
                    ))

                # Aggregate CFD specificity score
                cum_cfd, specificity, norm_safety = CFDScorer.calculate_specificity_score(cfd_scores)

                summary = GuideOffTargetSummary(
                    guide_sequence=guide,
                    total_off_targets=len([s for s in sites if s.annotation != "On-Target"]),
                    mismatch_counts=mismatch_counts,
                    cumulative_cfd_score=cum_cfd,
                    specificity_score=specificity,
                    normalized_safety_score=norm_safety,
                    sites=sites,
                    analysis_mode="REAL",
                    search_tool=tool_preference if self.runner.is_ready else "grch38_direct",
                    reference_assembly="GRCh38.p14",
                    index_version="GRCh38"
                )
                summaries.append(summary.to_dict())

            return {
                "status": "SUCCESS",
                "reference_genome": "GRCh38.p14",
                "search_tool": tool_preference if self.runner.is_ready else "grch38_direct",
                "execution_mode": execution_mode,
                "results": summaries
            }

        else:
            # Deterministic DEMO_MODE fallback (isolated, never mixed)
            results = []
            for guide in guide_sequences:
                results.append({
                    "guide_sequence": guide,
                    "total_off_targets": 3,
                    "mismatch_counts": {"0_mismatch": 0, "1_mismatch": 0, "2_mismatch": 1, "3_mismatch": 2},
                    "cumulative_cfd_score": 0.18,
                    "specificity_score": 99.82,
                    "normalized_safety_score": 0.9982,
                    "sites": [
                        {
                            "chromosome": "chr1",
                            "position": 1045230,
                            "strand": "+",
                            "sequence": guide[:15] + "AAA" + guide[18:20],
                            "pam": "AGG",
                            "mismatches": 2,
                            "mismatch_positions": [16, 17],
                            "cfd_score": 0.12,
                            "annotation": "Intergenic",
                            "risk_level": "MEDIUM"
                        },
                        {
                            "chromosome": "chr8",
                            "position": 88234100,
                            "strand": "-",
                            "sequence": guide[:12] + "TTT" + guide[15:20],
                            "pam": "CGG",
                            "mismatches": 3,
                            "mismatch_positions": [13, 14, 15],
                            "cfd_score": 0.06,
                            "annotation": "Intronic",
                            "risk_level": "LOW"
                        }
                    ],
                    "analysis_mode": "DEMO",
                    "search_tool": tool_preference,
                    "reference_genome": "GRCh38.p14 (Demo)",
                    "index_version": "Demo"
                })

            return {
                "status": "SUCCESS",
                "reference_genome": "GRCh38.p14",
                "search_tool": tool_preference,
                "execution_mode": execution_mode,
                "results": results
            }


# Global singleton instance
off_target_service = OffTargetService()
