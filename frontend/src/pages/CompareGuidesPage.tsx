import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GitCompareArrows, CheckSquare, Square, ArrowRight } from 'lucide-react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import { SectionHeader } from '../components/common/SectionHeader';
import { ModeBadge } from '../components/common/ModeBadge';
import { useHealth } from '../hooks/useHealth';
import { analysisStorage, StoredAnalysisRun } from '../services/analysisStorage';
import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';
import { WorkflowNavigationFooter } from '../components/common/WorkflowNavigationFooter';

export const CompareGuidesPage: React.FC = () => {
  const navigate = useNavigate();
  const { health } = useHealth();
  const [latestRun, setLatestRun] = useState<StoredAnalysisRun | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  useEffect(() => {
    const run = analysisStorage.getLatest();
    setLatestRun(run);
    if (run && run.rankedGuides && run.rankedGuides.length > 0) {
      const topIds = run.rankedGuides.slice(0, 2).map((g) => `Guide RNA ${g.rank}`);
      setSelectedIds(topIds);
    }
  }, []);

  const availableGuides = (latestRun?.rankedGuides || []).map((g) => ({
    id: `Guide RNA ${g.rank}`,
    sequence: g.protospacer_sequence,
    pam: g.pam,
    gc: ((g.gc_content ?? g.gc_percentage) || 50.0),
    onTarget: g.on_target_criterion,
    offTarget: g.off_target_criterion,
    cancerRel: g.cancer_relevance_criterion,
    gcOpt: g.gc_optimality_criterion,
    topsis: g.closeness_score,
    rank: g.rank,
  }));

  const toggleSelect = (id: string) => {
    if (selectedIds.includes(id)) {
      if (selectedIds.length > 1) {
        setSelectedIds(selectedIds.filter((x) => x !== id));
      }
    } else {
      if (selectedIds.length < 4) {
        setSelectedIds([...selectedIds, id]);
      }
    }
  };

  const selectedGuides = availableGuides.filter((g) => selectedIds.includes(g.id));

  // Radar chart multi-criteria data
  const radarData = [
    {
      criterion: 'On-Target Efficiency (35%)',
      ...Object.fromEntries(selectedGuides.map((g) => [g.id, g.onTarget * 100])),
    },
    {
      criterion: 'Off-Target Safety (30%)',
      ...Object.fromEntries(selectedGuides.map((g) => [g.id, g.offTarget * 100])),
    },
    {
      criterion: 'Cancer Relevance (20%)',
      ...Object.fromEntries(selectedGuides.map((g) => [g.id, g.cancerRel * 100])),
    },
    {
      criterion: 'GC Content Optimality (15%)',
      ...Object.fromEntries(selectedGuides.map((g) => [g.id, g.gcOpt * 100])),
    },
  ];

  const colors = ['#22d3ee', '#f59e0b', '#34d399', '#f43f5e'];

  return (
    <div className="relative w-full px-4 sm:px-6 lg:px-8 py-6 space-y-6 fade-in">
      <ScientificMolecularBackground intensity={0.55} />

      {/* Header */}
      <div className="research-card p-6 border-slate-800 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950/90">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                Comparative Analytics
              </span>
              <ModeBadge mode={health?.execution_mode || 'REAL_MODE'} />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <GitCompareArrows className="w-7 h-7 text-cyan-400" />
              <span>Multi-Guide Comparative Analysis</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              {latestRun
                ? `Head-to-head comparison of candidate guide RNAs for ${latestRun.gene} (${latestRun.cancer}) across biophysical properties, on-target predicted efficiencies, and off-target safety trade-offs.`
                : 'Head-to-head comparison of candidate gRNA biophysical properties, on-target predicted efficiencies, and off-target safety trade-offs.'}
            </p>
          </div>
        </div>
      </div>

      {/* Guide Selection Strip */}
      {availableGuides.length === 0 ? (
        <div className="research-card p-12 text-center text-slate-500 font-mono text-xs border border-dashed border-slate-800 rounded-lg space-y-3">
          <GitCompareArrows className="w-10 h-10 text-slate-600 mx-auto opacity-50" />
          <div className="text-sm font-bold text-slate-300">No analysis has been completed yet.</div>
          <div className="text-slate-400 max-w-md mx-auto leading-relaxed">
            Execute a full computational CRISPR guide design run in the Analysis Pipeline to enable multi-guide comparative analysis.
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
        <>
          {/* Guide Selector Chips */}
          <div className="research-card p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Select Candidates to Compare ({selectedIds.length}/4 Selected &bull; Target: {latestRun?.gene})
              </span>
              <span className="text-[11px] text-slate-400 font-mono">
                Click chips to toggle selection
              </span>
            </div>

            <div className="flex flex-wrap gap-2">
              {availableGuides.map((g) => {
                const isSelected = selectedIds.includes(g.id);
                return (
                  <button
                    key={g.id}
                    onClick={() => toggleSelect(g.id)}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-bold border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50'
                        : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'
                    }`}
                  >
                    {isSelected ? <CheckSquare size={13} /> : <Square size={13} />}
                    <span>{g.id} (#{g.rank})</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Radar Chart Multi-Attribute Comparison */}
            <div className="research-card p-5">
              <SectionHeader
                title="Multi-Attribute Radar Profile"
                subtitle="Four TOPSIS criteria breakdown across compared guide candidates"
              />

              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis dataKey="criterion" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                    <PolarRadiusAxis stroke="#475569" domain={[0, 100]} />
                    {selectedGuides.map((g, i) => (
                      <Radar
                        key={g.id}
                        name={g.id}
                        dataKey={g.id}
                        stroke={colors[i % colors.length]}
                        fill={colors[i % colors.length]}
                        fillOpacity={0.25}
                      />
                    ))}
                    <Legend wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0f172a',
                        borderColor: '#334155',
                        fontSize: '11px',
                        borderRadius: '8px',
                      }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Bar Chart TOPSIS and On-Target Comparison */}
            <div className="research-card p-5">
              <SectionHeader
                title="TOPSIS Score &amp; Efficiency Breakdown"
                subtitle="Normalized relative closeness and predicted on-target efficiency comparison"
              />

              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={selectedGuides}>
                    <XAxis dataKey="id" stroke="#64748b" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
                    <YAxis stroke="#64748b" domain={[0, 1.0]} tick={{ fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0f172a',
                        borderColor: '#334155',
                        fontSize: '11px',
                        borderRadius: '8px',
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
                    <Bar dataKey="topsis" name="TOPSIS Score" fill="#22d3ee" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="onTarget" name="Predicted On-Target" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="offTarget" name="Off-Target Safety" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Comparison Matrix Table */}
          <div className="research-card p-5">
            <SectionHeader
              title="Comparative Metrics Matrix"
              subtitle="Detailed head-to-head biophysical and computational prediction attributes"
            />

            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Candidate Guide</th>
                    <th>Protospacer (5&apos; &rarr; 3&apos;)</th>
                    <th>PAM</th>
                    <th>GC %</th>
                    <th>Predicted On-Target</th>
                    <th>Off-Target Safety</th>
                    <th>Cancer Relevance</th>
                    <th>TOPSIS Score</th>
                    <th>Rank</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedGuides.map((g) => (
                    <tr key={g.id}>
                      <td className="font-bold text-white font-mono">{g.id}</td>
                      <td className="font-mono text-cyan-400 font-semibold">{g.sequence}</td>
                      <td className="font-mono text-amber-400 font-bold">{g.pam}</td>
                      <td className="font-mono text-slate-200">{g.gc.toFixed(1)}%</td>
                      <td className="font-mono text-slate-200">{g.onTarget.toFixed(2)}</td>
                      <td className="font-mono text-slate-200">{g.offTarget.toFixed(2)}</td>
                      <td className="font-mono text-slate-200">{g.cancerRel.toFixed(2)}</td>
                      <td className="font-mono font-bold text-emerald-400">{g.topsis.toFixed(4)}</td>
                      <td className="font-mono font-bold text-cyan-400">#{g.rank}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Workflow Navigation Footer (Requirement 22: Off-Target -> Compare Guides -> Reports) */}
      <WorkflowNavigationFooter
        prevPath="/off-target"
        prevLabel="← Off-Target Analysis"
        nextPath="/reports"
        nextLabel="Next: Reports &amp; Export →"
      />
    </div>
  );
};
