import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Award, RotateCcw, ArrowRight } from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { ModeBadge } from '../components/common/ModeBadge';
import { useHealth } from '../hooks/useHealth';
import { TOPSISRankedItem } from '../types';
import { analysisStorage, StoredAnalysisRun } from '../services/analysisStorage';
import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';
import { WorkflowNavigationFooter } from '../components/common/WorkflowNavigationFooter';

export const TOPSISRankingPage: React.FC = () => {
  const navigate = useNavigate();
  const { health } = useHealth();
  const [latestRun, setLatestRun] = useState<StoredAnalysisRun | null>(null);

  // Dynamic Weights Configuration
  const [wOnTarget, setWOnTarget] = useState<number>(0.35);
  const [wOffTarget, setWOffTarget] = useState<number>(0.30);
  const [wCancer, setWCancer] = useState<number>(0.20);
  const [wGC, setWGC] = useState<number>(0.15);

  useEffect(() => {
    setLatestRun(analysisStorage.getLatest());
  }, []);

  // Compute live TOPSIS ranking from real candidates when weights change
  const rankedCandidates = useMemo<TOPSISRankedItem[]>(() => {
    if (!latestRun || !latestRun.rankedGuides || latestRun.rankedGuides.length === 0) {
      return [];
    }

    const items = latestRun.rankedGuides;
    const m = items.length;
    if (m === 0) return [];

    const sumW = wOnTarget + wOffTarget + wCancer + wGC || 1.0;
    const normW = [wOnTarget / sumW, wOffTarget / sumW, wCancer / sumW, wGC / sumW];

    // Extract raw matrix: [C1, C2, C3, C4]
    const rawMatrix = items.map((it) => [
      it.on_target_criterion,
      it.off_target_criterion,
      it.cancer_relevance_criterion,
      it.gc_optimality_criterion,
    ]);

    // Vector normalization denominators
    const denom = [0, 0, 0, 0];
    for (let j = 0; j < 4; j++) {
      let sumSq = 0;
      for (let i = 0; i < m; i++) {
        sumSq += rawMatrix[i][j] * rawMatrix[i][j];
      }
      denom[j] = Math.sqrt(sumSq) || 1.0;
    }

    // Weighted normalized matrix
    const vMatrix = rawMatrix.map((row) =>
      row.map((val, j) => normW[j] * (val / denom[j]))
    );

    // Positive and Negative Ideal Solutions
    const aPos = [0, 0, 0, 0];
    const aNeg = [0, 0, 0, 0];
    for (let j = 0; j < 4; j++) {
      let colMax = -Infinity;
      let colMin = Infinity;
      for (let i = 0; i < m; i++) {
        const v = vMatrix[i][j];
        if (v > colMax) colMax = v;
        if (v < colMin) colMin = v;
      }
      aPos[j] = colMax;
      aNeg[j] = colMin;
    }

    // Euclidean distances and closeness scores
    const evaluated = items.map((it, i) => {
      let dPosSq = 0;
      let dNegSq = 0;
      for (let j = 0; j < 4; j++) {
        const v = vMatrix[i][j];
        dPosSq += Math.pow(v - aPos[j], 2);
        dNegSq += Math.pow(v - aNeg[j], 2);
      }
      const sPos = Math.sqrt(dPosSq);
      const sNeg = Math.sqrt(dNegSq);
      const closeness = sPos + sNeg > 0 ? sNeg / (sPos + sNeg) : 0;

      return {
        ...it,
        distance_positive_ideal: Number(sPos.toFixed(4)),
        distance_negative_ideal: Number(sNeg.toFixed(4)),
        closeness_score: Number(closeness.toFixed(4)),
      };
    });

    // Sort descending by closeness score
    evaluated.sort((a, b) => b.closeness_score - a.closeness_score);
    const result = evaluated.map((it, idx) => ({ ...it, rank: idx + 1 }));
    analysisStorage.updateLatestRankedGuides(result);
    return result;
  }, [latestRun, wOnTarget, wOffTarget, wCancer, wGC]);

  const resetWeights = () => {
    setWOnTarget(0.35);
    setWOffTarget(0.30);
    setWCancer(0.20);
    setWGC(0.15);
  };

  return (
    <div className="relative w-full px-4 sm:px-6 lg:px-8 py-6 space-y-6 fade-in">
      <ScientificMolecularBackground intensity={0.55} />

      {/* Header */}
      <div className="research-card p-6 border-slate-800 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950/90">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                Mathematical Decision &bull; Stage 05
              </span>
              <ModeBadge mode={health?.execution_mode || 'REAL_MODE'} />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <Award className="w-7 h-7 text-cyan-400" />
              <span>TOPSIS Multi-Criteria Decision Ranking</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              {latestRun
                ? `Vector-normalized multi-criteria decision matrix evaluating candidates for ${latestRun.gene} (${latestRun.cancer}) based on Euclidean distance to positive and negative ideal solutions.`
                : 'Technique for Order Preference by Similarity to Ideal Solution (TOPSIS) evaluating vector-normalized Euclidean distances to positive and negative ideal solutions.'}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate('/analysis-pipeline')}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors cursor-pointer"
            >
              <span>Start New Analysis</span>
            </button>
            {rankedCandidates.length > 0 && (
              <button
                onClick={() => navigate('/ranked-guides')}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
              >
                <span>View Ranked Guides</span>
                <ArrowRight size={14} />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Criteria Weight Customizer */}
      <div className="research-card p-5 space-y-4">
        <SectionHeader
          title="Multi-Criteria Weight Optimization"
          subtitle="Adjust relative importance weights across 4 decision criteria (Normalized Sum: 1.00)"
          action={
            <button
              onClick={resetWeights}
              className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-white bg-slate-800 px-2.5 py-1.5 rounded-lg border border-slate-700 transition-colors cursor-pointer"
            >
              <RotateCcw size={12} />
              <span>Reset Defaults</span>
            </button>
          }
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* C1: On-Target */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-cyan-400">On-Target Efficiency</span>
              <span className="font-mono font-bold text-white">{(wOnTarget * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.70"
              step="0.05"
              value={wOnTarget}
              onChange={(e) => setWOnTarget(Number(e.target.value))}
              className="w-full accent-cyan-400 cursor-pointer"
            />
            <p className="text-[10px] text-slate-400">Hybrid prediction model efficiency score.</p>
          </div>

          {/* C2: Off-Target */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-emerald-400">Off-Target Safety</span>
              <span className="font-mono font-bold text-white">{(wOffTarget * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.70"
              step="0.05"
              value={wOffTarget}
              onChange={(e) => setWOffTarget(Number(e.target.value))}
              className="w-full accent-emerald-400 cursor-pointer"
            />
            <p className="text-[10px] text-slate-400">GRCh38 CFD cutting frequency specificity score.</p>
          </div>

          {/* C3: Cancer Relevance */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-amber-400">Cancer Relevance</span>
              <span className="font-mono font-bold text-white">{(wCancer * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.70"
              step="0.05"
              value={wCancer}
              onChange={(e) => setWCancer(Number(e.target.value))}
              className="w-full accent-amber-400 cursor-pointer"
            />
            <p className="text-[10px] text-slate-400">TCGA expression profile and target essentiality index.</p>
          </div>

          {/* C4: GC Optimality */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-purple-400">GC Optimality</span>
              <span className="font-mono font-bold text-white">{(wGC * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.70"
              step="0.05"
              value={wGC}
              onChange={(e) => setWGC(Number(e.target.value))}
              className="w-full accent-purple-400 cursor-pointer"
            />
            <p className="text-[10px] text-slate-400">Deviation penalty centered at 50% target GC fraction.</p>
          </div>
        </div>
      </div>

      {/* Decision Matrix & Final Rankings Table */}
      <div className="research-card p-5 space-y-4">
        <SectionHeader
          title="TOPSIS Decision Matrix &amp; Relative Closeness Scores"
          subtitle="Normalized criteria matrix and Euclidean distances to positive (S⁺) and negative (S⁻) ideal solutions"
        />

        {rankedCandidates.length === 0 ? (
          <div className="py-16 text-center text-slate-500 font-mono text-xs border border-dashed border-slate-800 rounded-lg space-y-3">
            <Award className="w-8 h-8 text-slate-600 mx-auto opacity-50" />
            <div className="text-sm font-bold text-slate-400">No analysis has been completed yet.</div>
            <div className="text-[11px] text-slate-500 max-w-md mx-auto">
              TOPSIS decision ranking calculates multi-criteria trade-offs from a completed analysis pipeline run.
            </div>
            <button
              onClick={() => navigate('/analysis-pipeline')}
              className="mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
            >
              <span>Start New Analysis &rarr;</span>
              <ArrowRight size={13} />
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Candidate Guide</th>
                  <th>Protospacer (5&apos; &rarr; 3&apos;)</th>
                  <th>PAM</th>
                  <th>On-Target Efficiency</th>
                  <th>Off-Target Safety</th>
                  <th>Cancer Relevance</th>
                  <th>GC Content Optimality</th>
                  <th>Ideal Distance (S⁺)</th>
                  <th>Anti-Ideal Distance (S⁻)</th>
                  <th>TOPSIS Score</th>
                </tr>
              </thead>
              <tbody>
                {rankedCandidates.map((g) => (
                  <tr key={g.guide_id || g.protospacer_sequence}>
                    <td className="font-bold font-mono text-cyan-400 text-sm">
                      {g.rank === 1 ? '🥇 #1' : g.rank === 2 ? '🥈 #2' : g.rank === 3 ? '🥉 #3' : `#${g.rank}`}
                    </td>
                    <td className="font-mono text-slate-200 font-semibold">Guide RNA {g.rank}</td>
                    <td className="font-mono text-white font-bold tracking-wider">{g.protospacer_sequence}</td>
                    <td className="font-mono text-amber-400 font-extrabold">{g.pam}</td>
                    <td className="font-mono text-slate-300">{g.on_target_criterion.toFixed(3)}</td>
                    <td className="font-mono text-slate-300">{g.off_target_criterion.toFixed(3)}</td>
                    <td className="font-mono text-slate-300">{g.cancer_relevance_criterion.toFixed(3)}</td>
                    <td className="font-mono text-slate-300">{g.gc_optimality_criterion.toFixed(3)}</td>
                    <td className="font-mono text-slate-400">{g.distance_positive_ideal.toFixed(4)}</td>
                    <td className="font-mono text-slate-400">{g.distance_negative_ideal.toFixed(4)}</td>
                    <td className="font-mono font-extrabold text-emerald-400 text-sm">
                      {g.closeness_score.toFixed(4)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Workflow Navigation Footer (Requirement 22: Design Studio -> TOPSIS -> Ranked Guides) */}
      <WorkflowNavigationFooter
        prevPath="/design-studio"
        prevLabel="← 3D Design Studio"
        nextPath="/ranked-guides"
        nextLabel="Next: Ranked Guide RNAs →"
      />
    </div>
  );
};
