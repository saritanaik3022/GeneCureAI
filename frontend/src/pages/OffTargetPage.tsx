import React, { useState, useEffect } from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle, Database, Search } from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { ModeBadge } from '../components/common/ModeBadge';
import { MetricCard } from '../components/common/MetricCard';
import { analyzeOffTarget } from '../services/api';
import { analysisStorage, StoredAnalysisRun } from '../services/analysisStorage';
import { useHealth } from '../hooks/useHealth';
import { OffTargetResponse } from '../types';
import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';
import { WorkflowNavigationFooter } from '../components/common/WorkflowNavigationFooter';

export const OffTargetPage: React.FC = () => {
  const { health } = useHealth();
  const [latestRun] = useState<StoredAnalysisRun | null>(() => analysisStorage.getLatest());
  const [guideInput, setGuideInput] = useState<string>(() => {
    return latestRun?.topGuide && latestRun.topGuide.length === 20
      ? latestRun.topGuide
      : 'GCAGCCAGATGCCTGGACAG';
  });
  const [data, setData] = useState<OffTargetResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluatedGuide, setEvaluatedGuide] = useState<string>('');

  const handleAnalyze = (seq?: string) => {
    const targetSeq = (seq || guideInput).trim().toUpperCase();
    if (!targetSeq || targetSeq.length !== 20) {
      setError('Please provide a valid 20-nt CRISPR guide RNA protospacer sequence.');
      return;
    }
    setLoading(true);
    setError(null);
    setEvaluatedGuide(targetSeq);

    analyzeOffTarget({ guide_sequences: [targetSeq] })
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Off-target query failed', err);
        setError(err.message || 'Failed to complete GRCh38 off-target analysis.');
        setLoading(false);
      });
  };

  useEffect(() => {
    handleAnalyze();
  }, []);

  const result = data?.results?.[0];

  return (
    <div className="relative w-full px-4 sm:px-6 lg:px-8 py-6 space-y-6 fade-in">
      <ScientificMolecularBackground intensity={0.55} />

      {/* Header */}
      <div className="research-card p-6 border-slate-800 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950/90">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                Stage 04 &bull; Specificity Evaluation
              </span>
              <ModeBadge mode={health?.execution_mode || 'REAL_MODE'} />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <ShieldAlert className="w-7 h-7 text-cyan-400" />
              <span>Computational Off-Target Safety Analysis</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Genome-wide (GRCh38) seed-and-extend mismatch alignment and Cutting Frequency Determination (CFD) cutting frequency score calculation.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="text"
              value={guideInput}
              onChange={(e) => setGuideInput(e.target.value.toUpperCase())}
              placeholder="Enter 20-nt guide..."
              maxLength={20}
              className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-cyan-400 focus:outline-none focus:border-cyan-500 w-56"
            />
            <button
              onClick={() => handleAnalyze()}
              disabled={loading}
              className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 rounded-lg text-xs font-bold uppercase tracking-wider cursor-pointer transition-all disabled:opacity-50"
            >
              {loading ? 'Searching...' : 'Analyze Guide'}
            </button>
          </div>
        </div>
      </div>

      {/* Guide Quick Select from Current Run if available */}
      {latestRun && latestRun.rankedGuides && latestRun.rankedGuides.length > 0 && (
        <div className="research-card p-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Guides from Current Run ({latestRun.gene} &bull; {latestRun.cancer || 'Cancer Analysis'}):
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {latestRun.rankedGuides.slice(0, 5).map((g, idx) => (
              <button
                key={g.protospacer_sequence}
                onClick={() => {
                  setGuideInput(g.protospacer_sequence);
                  handleAnalyze(g.protospacer_sequence);
                }}
                disabled={loading}
                className={`px-2.5 py-1 rounded text-xs font-mono font-semibold border transition-all cursor-pointer ${
                  guideInput === g.protospacer_sequence
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/60'
                    : 'bg-slate-900 hover:bg-slate-800 text-slate-400 border-slate-800'
                }`}
              >
                Guide RNA {idx + 1} ({g.protospacer_sequence.slice(0, 8)}...)
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Error alert banner if analysis failed */}
      {error && (
        <div className="p-4 rounded-lg bg-red-950/60 border border-red-800/80 text-red-300 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs font-mono">
            <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={() => handleAnalyze()}
            className="px-3 py-1 bg-red-900/60 hover:bg-red-800 text-red-200 rounded text-xs font-mono font-bold cursor-pointer transition-colors"
          >
            Retry Analysis
          </button>
        </div>
      )}

      {/* Genome Resource Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="GRCh38 Reference"
          value="Online"
          subtitle="Human Genome Primary Assembly"
          icon={<Database size={15} style={{ color: '#34d399' }} />}
          accent="green"
        />

        <MetricCard
          label="Specificity Score"
          value={result ? `${result.specificity_score.toFixed(2)}%` : loading ? 'Computing...' : '--'}
          subtitle="100 / (1.0 + Σ CFD_i)"
          icon={<ShieldCheck size={15} style={{ color: '#22d3ee' }} />}
          accent="cyan"
        />

        <MetricCard
          label="Cumulative CFD"
          value={result ? result.cumulative_cfd_score.toFixed(4) : loading ? 'Computing...' : '--'}
          subtitle="Summed cleavage penalty index"
          icon={<AlertTriangle size={15} style={{ color: '#f59e0b' }} />}
          accent="amber"
        />

        <MetricCard
          label="Off-Target Matches"
          value={result ? result.total_off_targets.toString() : loading ? 'Searching...' : '--'}
          subtitle="Identified genomic mismatch loci"
          icon={<Search size={15} style={{ color: '#60a5fa' }} />}
          accent="blue"
        />
      </div>

      {/* Mismatch Loci Breakdown Table */}
      <div className="research-card p-5">
        <SectionHeader
          title="Predicted Genomic Off-Target Sites"
          subtitle="Identified mismatch loci across chromosomes with individual CFD cutting frequency weights"
          action={
            <span className="text-xs font-mono text-slate-400">
              Evaluated Guide: <strong className="text-cyan-400">{evaluatedGuide || guideInput}</strong>
            </span>
          }
        />

        {loading ? (
          <div className="text-center py-12 text-slate-400 text-xs font-mono flex flex-col items-center justify-center gap-2">
            <div className="w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
            <span>Searching GRCh38 genomic indices for off-target loci and evaluating CFD weights...</span>
          </div>
        ) : !result || result.sites.length === 0 ? (
          <div className="py-12 text-center text-slate-400 font-mono text-xs border border-dashed border-slate-800 rounded-lg space-y-2">
            <div className="text-sm font-semibold text-slate-200">
              No significant off-target matches identified in the evaluated GRCh38 search.
            </div>
            <div className="text-[11px] text-slate-400">
              Guide displays maximal genomic specificity against the GRCh38 human genome assembly.
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Chromosome</th>
                  <th>Genomic Position</th>
                  <th>Strand</th>
                  <th>Off-Target Sequence</th>
                  <th>PAM</th>
                  <th>Mismatches</th>
                  <th>Mismatch Positions</th>
                  <th>CFD Score</th>
                  <th>Annotation</th>
                  <th>Risk Tier</th>
                </tr>
              </thead>
              <tbody>
                {result.sites.map((site, idx) => (
                  <tr key={idx}>
                    <td className="font-bold text-white font-mono">{site.chromosome}</td>
                    <td className="font-mono text-slate-300">{site.position.toLocaleString()}</td>
                    <td className="font-mono font-bold">{site.strand}</td>
                    <td className="font-mono text-slate-200 tracking-wider">{site.sequence}</td>
                    <td className="font-mono text-amber-400 font-bold">{site.pam}</td>
                    <td className="font-mono font-bold text-slate-100">{site.mismatches} bp</td>
                    <td className="font-mono text-[11px] text-slate-400">
                      [{site.mismatch_positions.join(', ')}]
                    </td>
                    <td className="font-mono font-bold text-amber-400">{site.cfd_score.toFixed(4)}</td>
                    <td className="text-slate-300">{site.annotation}</td>
                    <td>
                      <span
                        className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                          site.cfd_score > 0.1
                            ? 'bg-amber-950 text-amber-300 border border-amber-800'
                            : 'bg-slate-900 text-slate-400'
                        }`}
                      >
                        {site.cfd_score > 0.1 ? 'Moderate Risk' : 'Low Risk'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Workflow Navigation Footer (Requirement 22: Ranked Guides -> Off-Target -> Compare Guides) */}
      <WorkflowNavigationFooter
        prevPath="/ranked-guides"
        prevLabel="← Ranked Guide RNAs"
        nextPath="/compare-guides"
        nextLabel="Next: Compare Guides →"
      />
    </div>
  );
};
