import React from 'react';
import { BookOpen, Dna, Activity, ShieldCheck, Award, Target } from 'lucide-react';

import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';

export const MethodologyPage: React.FC = () => {
  return (
    <div className="relative w-full px-4 sm:px-6 lg:px-8 py-6 space-y-6 fade-in">
      <ScientificMolecularBackground intensity={0.55} />
      {/* Header */}
      <div className="research-card p-6 border-slate-800 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950/90">
        <div className="max-w-3xl space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
              Scientific Reference &amp; Mathematical Formulation
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <BookOpen className="w-7 h-7 text-cyan-400" />
            <span>Methodology &amp; Algorithmic Architecture</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            A comprehensive overview of the biological databases, deep learning topologies, 105-feature engineering principles, and multi-criteria decision ranking formulating Gene-Cure AI.
          </p>
        </div>
      </div>



      {/* 5 Stages Scientific Detail */}
      <div className="space-y-6">
        {/* Stage 1 */}
        <div className="research-card p-6 space-y-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Target size={20} />
            </div>
            <div>
              <span className="text-xs font-mono font-bold text-cyan-400">Stage 01</span>
              <h2 className="text-base font-bold text-white">Cancer Gene Selection &amp; CDS Ingestion</h2>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            The platform targets 9 clinically validated oncogenes and tumor suppressors across Breast cancer (<strong>BRCA1</strong>, <strong>HER2</strong>, <strong>TP53</strong>), Lung cancer (<strong>EGFR</strong>, <strong>KRAS</strong>, <strong>ALK</strong>), and Liver cancer (<strong>CTNNB1</strong>, <strong>AXIN1</strong>, <strong>TERT</strong>). Genomic coordinates, exon boundaries, and canonical coding sequences (CDS) are ingested from Ensembl Release 112 (GENCODE v46) and verified against NCBI Gene ID / HGNC registries on the GRCh38.p14 reference assembly.
          </p>
        </div>

        {/* Stage 2 */}
        <div className="research-card p-6 space-y-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <Dna size={20} />
            </div>
            <div>
              <span className="text-xs font-mono font-bold text-blue-400">Stage 02</span>
              <h2 className="text-base font-bold text-white">SpCas9 In-Silico Guide RNA Discovery</h2>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Scans both the sense (5&apos; &rarr; 3&apos;) and antisense (3&apos; &rarr; 5&apos;) strands of the target CDS for the canonical <em>Streptococcus pyogenes</em> Cas9 (SpCas9) Protospacer Adjacent Motif (<strong>5&apos;-NGG-3&apos;</strong>). For each PAM site, extracts a 20-nt protospacer along with an extended 30-nt context (4-nt 5&apos; flank + 20-nt guide + 3-nt PAM + 3-nt 3&apos; flank) required for downstream deep learning and thermodynamic feature modeling.
          </p>
        </div>

        {/* Stage 3 */}
        <div className="research-card p-6 space-y-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Activity size={20} />
            </div>
            <div>
              <span className="text-xs font-mono font-bold text-indigo-400">Stage 03</span>
              <h2 className="text-base font-bold text-white">Hybrid On-Target Efficiency Prediction (CNN + XGBoost)</h2>
            </div>
          </div>
          <div className="space-y-2 text-xs text-slate-300 leading-relaxed">
            <p>
              On-target cleavage efficacy is predicted via a dual-branch hybrid stacking architecture trained on the 5,311 sgRNA knockout screens from Doench et al. (Nat Biotechnol. 2016):
            </p>
            <ul className="list-disc pl-5 space-y-1 text-slate-400">
              <li>
                <strong>Branch A (PyTorch 1D-CNN):</strong> Direct (4 &times; 30) one-hot sequence matrix processed through Conv1D(64), BatchNorm, LeakyReLU, Conv1D(128), MaxPool1D, and dense layers with dropout regularization.
              </li>
              <li>
                <strong>Branch B (XGBoost Regressor):</strong> 105 engineered biophysical features including position-specific single nucleotides (28), dinucleotide interactions (56), regional GC content (8), nearest-neighbor melting temperatures Tm and enthalpy proxies (8), and sequence complexity homopolymer penalties (5).
              </li>
              <li>
                <strong>Ensemble Meta-Learner:</strong> Stacking linear regression calibrating final on-target efficiency E &isin; [0.0, 1.0].
              </li>
            </ul>
          </div>
        </div>

        {/* Stage 4 */}
        <div className="research-card p-6 space-y-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <ShieldCheck size={20} />
            </div>
            <div>
              <span className="text-xs font-mono font-bold text-emerald-400">Stage 04</span>
              <h2 className="text-base font-bold text-white">GRCh38 Off-Target Specificity &amp; CFD Scoring</h2>
            </div>
          </div>
          <div className="space-y-2 text-xs text-slate-300 leading-relaxed">
            <p>
              Potential off-target cleavage sites are mapped against the complete GRCh38.p14 human genome using Bowtie2 seed-and-extend alignment (allowing up to 3 mismatches in the 12-nt PAM-proximal seed, 6 total).
            </p>
            <p>
              Each candidate locus is scored via the Cutting Frequency Determination (CFD) matrix:
            </p>
            <div className="p-3 bg-slate-950 font-mono text-cyan-400 rounded-lg border border-slate-800 text-center">
              CFD_site = &prod; M(pos, r_pos, a_pos) &times; P(PAM)
            </div>
            <p>
              The composite guide specificity score is calculated as:
            </p>
            <div className="p-3 bg-slate-950 font-mono text-emerald-400 rounded-lg border border-slate-800 text-center">
              Specificity Score = 100 / (100 + &sum; CFD_i) &isin; [0, 100]
            </div>
          </div>
        </div>

        {/* Stage 5 */}
        <div className="research-card p-6 space-y-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <Award size={20} />
            </div>
            <div>
              <span className="text-xs font-mono font-bold text-amber-400">Stage 05</span>
              <h2 className="text-base font-bold text-white">TOPSIS Multi-Criteria Guide Ranking</h2>
            </div>
          </div>
          <div className="space-y-2 text-xs text-slate-300 leading-relaxed">
            <p>
              Candidate guide RNAs are prioritized using the Technique for Order Preference by Similarity to Ideal Solution (TOPSIS) across 4 normalized benefit criteria:
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-[11px] text-center my-2">
              <div className="p-2 rounded bg-slate-900 border border-slate-800 text-cyan-400">
                On-Target (w1 = 0.35)
              </div>
              <div className="p-2 rounded bg-slate-900 border border-slate-800 text-emerald-400">
                Off-Target (w2 = 0.30)
              </div>
              <div className="p-2 rounded bg-slate-900 border border-slate-800 text-amber-400">
                Cancer Rel. (w3 = 0.20)
              </div>
              <div className="p-2 rounded bg-slate-900 border border-slate-800 text-purple-400">
                GC Opt. (w4 = 0.15)
              </div>
            </div>
            <p>
              Relative closeness coefficient to the positive ideal solution (A+) determines the final rank:
            </p>
            <div className="p-3 bg-slate-950 font-mono text-cyan-400 rounded-lg border border-slate-800 text-center">
              C_i = S_i^- / (S_i^+ + S_i^-) &isin; [0, 1]
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
