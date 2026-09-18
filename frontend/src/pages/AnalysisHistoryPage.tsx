import React, { useState, useEffect } from 'react';
import { History, Search } from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { ModeBadge } from '../components/common/ModeBadge';
import { StatusBadge } from '../components/common/StatusBadge';

import { useHealth } from '../hooks/useHealth';
import { analysisStorage, StoredAnalysisRun } from '../services/analysisStorage';
import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';

export const AnalysisHistoryPage: React.FC = () => {
  const { health } = useHealth();
  const [searchTerm, setSearchTerm] = useState('');
  const [cancerFilter, setCancerFilter] = useState('ALL');
  const [historyRecords, setHistoryRecords] = useState<StoredAnalysisRun[]>([]);

  useEffect(() => {
    setHistoryRecords(analysisStorage.getHistory());
  }, []);

  // handleClear is available for future use:
  // const handleClear = () => { analysisStorage.clearHistory(); setHistoryRecords([]); };

  const filtered = historyRecords.filter((r) => {
    const matchesSearch =
      r.runId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.gene.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.topGuide.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCancer = cancerFilter === 'ALL' || r.cancer === cancerFilter;
    return matchesSearch && matchesCancer;
  });

  return (
    <div className="relative w-full px-4 sm:px-6 lg:px-8 py-6 space-y-6 fade-in">
      <ScientificMolecularBackground intensity={0.55} />
      {/* Header */}
      <div className="research-card p-6 border-slate-800 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950/90">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                Audit Trail &amp; Provenance
              </span>
              <ModeBadge mode={health?.execution_mode || 'REAL_MODE'} />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <History className="w-7 h-7 text-cyan-400" />
              <span>Computational Analysis History</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Audit logs of previous in-silico CRISPR guide RNA design runs with complete provenance, parameters, and top-ranked candidates.
            </p>
          </div>
        </div>
      </div>



      {/* Filter / Search Bar */}
      <div className="research-card p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search by Run ID, Gene, Guide..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-64"
            />
          </div>

          <select
            value={cancerFilter}
            onChange={(e) => setCancerFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Cancer Types</option>
            <option value="Breast cancer">Breast cancer</option>
            <option value="Lung cancer">Lung cancer</option>
            <option value="Liver cancer">Liver cancer</option>
          </select>
        </div>

        <div className="text-xs text-slate-400">
          Showing <strong className="text-white font-mono">{filtered.length}</strong> analysis records
        </div>
      </div>

      {/* History Table */}
      <div className="research-card p-5">
        <SectionHeader
          title="Analysis Runs Log"
          subtitle="Timestamped records of completed computational evaluations"
        />

        {filtered.length === 0 ? (
          <div className="py-16 text-center text-slate-500 font-mono text-xs border border-dashed border-slate-800 rounded-lg">
            <History className="w-8 h-8 text-slate-600 mx-auto mb-2 opacity-50" />
            <div>No completed analyses yet.</div>
            <div className="text-[11px] text-slate-500 mt-1">
              Analyses executed in the{' '}
              <a href="#/analysis-pipeline" className="text-cyan-400 hover:text-cyan-300 underline font-bold">
                Pipeline Wizard
              </a>{' '}
              will be permanently recorded in this audit log.
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Analysis ID</th>
                  <th>Target Cancer</th>
                  <th>Target Gene</th>
                  <th>Execution Date (UTC)</th>
                  <th>Mode</th>
                  <th>Candidates</th>
                  <th>Status</th>
                  <th>Top-Ranked Guide</th>
                  <th>PAM</th>
                  <th>TOPSIS Score</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((r) => (
                  <tr key={r.runId}>
                    <td className="font-mono text-cyan-400 font-semibold">{r.runId}</td>
                    <td>{r.cancer}</td>
                    <td className="font-bold text-white">{r.gene}</td>
                    <td className="text-slate-400 font-mono text-[11px]">{r.date}</td>
                    <td>
                      <ModeBadge mode={r.mode} />
                    </td>
                    <td className="font-mono">{r.candidateCount}</td>
                    <td>
                      <StatusBadge status={r.status} />
                    </td>
                    <td className="font-mono text-slate-200 tracking-wider text-xs">{r.topGuide}</td>
                    <td className="font-mono text-amber-400 font-bold">{r.pam}</td>
                    <td className="font-mono font-bold text-emerald-400">{r.topsisScore > 0 ? r.topsisScore.toFixed(4) : '--'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
