import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Award,
  Boxes,
  Dna,
  ArrowRight,
  Sparkles,
  Database,
  Eye,
  X,
  Download,
  Search,
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { ModeBadge } from '../components/common/ModeBadge';
import { StatusBadge } from '../components/common/StatusBadge';
import { useHealth } from '../hooks/useHealth';
import { analysisStorage, StoredAnalysisRun } from '../services/analysisStorage';
import { TOPSISRankedItem } from '../types';
import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';
import { WorkflowNavigationFooter } from '../components/common/WorkflowNavigationFooter';

export const RankedGuidesPage: React.FC = () => {
  const navigate = useNavigate();
  const { health } = useHealth();
  const [latestRun, setLatestRun] = useState<StoredAnalysisRun | null>(null);
  const [selectedGuideForModal, setSelectedGuideForModal] = useState<TOPSISRankedItem | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    setLatestRun(analysisStorage.getLatest());
  }, []);

  const rankedGuides = latestRun?.rankedGuides || [];

  const filteredGuides = useMemo(() => {
    if (!searchQuery.trim()) return rankedGuides;
    const q = searchQuery.toLowerCase().trim();
    return rankedGuides.filter(
      (g) =>
        g.protospacer_sequence?.toLowerCase().includes(q) ||
        g.pam?.toLowerCase().includes(q) ||
        (g.strand && g.strand.includes(q)) ||
        (g.rank != null && String(g.rank).includes(q)) ||
        (g.genomic_start != null && String(g.genomic_start).includes(q))
    );
  }, [rankedGuides, searchQuery]);

  const handleOpen3DTarget = (guide: TOPSISRankedItem) => {
    navigate('/design-studio', {
      state: {
        selectedGuide: guide,
        geneSymbol: latestRun?.gene || 'BRCA1',
        cancerType: latestRun?.cancer || 'Breast Cancer',
        autoStart: true,
      },
    });
  };

  // CSV Export for real ranked candidates (Requirement 21)
  const handleDownloadCSV = () => {
    if (!latestRun || rankedGuides.length === 0) return;

    const headers = [
      'Rank',
      'Guide RNA',
      'Protospacer Sequence',
      'PAM',
      'Strand',
      'Genomic Coordinate',
      'Exon',
      'GC Content (%)',
      'On-Target Efficiency',
      'Off-Target Safety',
      'Cancer Relevance',
      'GC Content Optimality',
      'TOPSIS Score',
    ];

    const exportList = filteredGuides.length > 0 ? filteredGuides : rankedGuides;
    const rows = exportList.map((g, idx) => [
      g.rank || idx + 1,
      `Guide RNA ${g.rank || idx + 1}`,
      g.protospacer_sequence,
      g.pam,
      g.strand || '+',
      g.genomic_start ? `chr${g.chromosome || ''}:${g.genomic_start}-${g.genomic_end || g.genomic_start + 23}` : 'N/A',
      g.exon_number ? `Exon ${g.exon_number}` : 'Exon 1',
      ((g.gc_content ?? g.gc_percentage) || 50.0).toFixed(1),
      g.on_target_criterion.toFixed(4),
      g.off_target_criterion.toFixed(4),
      g.cancer_relevance_criterion.toFixed(4),
      g.gc_optimality_criterion.toFixed(4),
      g.closeness_score.toFixed(4),
    ]);

    const csvContent = [
      `# Gene-Cure AI — Ranked CRISPR Guide RNA Report`,
      `# Target Gene: ${latestRun.gene} | Target Cancer: ${latestRun.cancer} | Date: ${latestRun.date}`,
      `# Reference Genome: GRCh38.p14 | Annotation: GENCODE v46 | Mode: ${latestRun.mode}`,
      headers.join(','),
      ...rows.map((r) => r.map((cell) => `"${cell}"`).join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `GeneCureAI_${latestRun.gene}_Ranked_Guides.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
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
                Pipeline Result &bull; Multi-Criteria Ranking
              </span>
              <ModeBadge mode={health?.execution_mode || 'REAL_MODE'} />
              {latestRun && <StatusBadge status="Analysis Completed" />}
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <Award className="w-7 h-7 text-cyan-400" />
              <span>Ranked Guide RNAs</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              {latestRun
                ? `Computationally ranked guide RNAs for ${latestRun.gene} (${latestRun.cancer}) across On-Target Efficiency, Off-Target Safety, Cancer Relevance, and GC Content Optimality.`
                : 'Computationally ranked guide RNAs across on-target efficiency, off-target safety, cancer relevance, and GC optimality.'}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => navigate('/analysis-pipeline')}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors cursor-pointer"
            >
              <Dna size={13} />
              <span>Start New Analysis</span>
            </button>
            {rankedGuides.length > 0 && (
              <>
                <button
                  onClick={handleDownloadCSV}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-bold bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-500/40 shadow-sm transition-all cursor-pointer"
                  title="Export ranked candidates to CSV"
                >
                  <Download size={13} />
                  <span>Download Ranked Guides &darr;</span>
                </button>
                <button
                  onClick={() => handleOpen3DTarget(rankedGuides[0])}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
                >
                  <Boxes size={14} />
                  <span>View Rank #1 in 3D Studio</span>
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Clean Empty State when no analysis has been executed */}
      {!latestRun || rankedGuides.length === 0 ? (
        <div className="research-card p-16 text-center text-slate-500 font-mono text-xs border border-dashed border-slate-800 rounded-xl space-y-4">
          <Award className="w-12 h-12 text-slate-600 mx-auto opacity-50" />
          <div className="text-base font-bold text-slate-300">No analysis has been completed yet.</div>
          <div className="text-slate-400 max-w-md mx-auto leading-relaxed">
            Execute a full computational CRISPR guide design run in the Analysis Pipeline to discover, score, and rank candidate guide RNAs for your target gene.
          </div>
          <button
            onClick={() => navigate('/analysis-pipeline')}
            className="mt-2 inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
          >
            <span>Start New Analysis &rarr;</span>
            <ArrowRight size={14} />
          </button>
        </div>
      ) : (
        <>
          {/* Summary Strip */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            <div className="research-card p-3 border-cyan-900/40 bg-cyan-950/20">
              <div className="text-[10px] text-cyan-400 font-mono font-bold uppercase">Target Gene</div>
              <div className="text-sm font-mono font-extrabold text-white mt-1">{latestRun.gene}</div>
            </div>
            <div className="research-card p-3 border-slate-800">
              <div className="text-[10px] text-slate-400 font-mono font-bold uppercase">Cancer Type</div>
              <div className="text-xs font-semibold text-slate-200 mt-1 truncate">{latestRun.cancer}</div>
            </div>
            <div className="research-card p-3 border-slate-800">
              <div className="text-[10px] text-slate-400 font-mono font-bold uppercase">Candidates Scanned</div>
              <div className="text-sm font-mono font-extrabold text-emerald-400 mt-1">
                {latestRun.candidateCount} gRNAs
              </div>
            </div>
            <div className="research-card p-3 border-slate-800">
              <div className="text-[10px] text-slate-400 font-mono font-bold uppercase">Top Candidate</div>
              <div className="text-xs font-mono font-bold text-cyan-300 mt-1 truncate">
                Guide RNA 1
              </div>
            </div>
            <div className="research-card p-3 border-slate-800">
              <div className="text-[10px] text-slate-400 font-mono font-bold uppercase">Top TOPSIS Score</div>
              <div className="text-sm font-mono font-extrabold text-emerald-400 mt-1">
                {rankedGuides[0]?.closeness_score.toFixed(4) || '--'}
              </div>
            </div>
            <div className="research-card p-3 border-slate-800">
              <div className="text-[10px] text-slate-400 font-mono font-bold uppercase flex items-center gap-1">
                <Database size={10} /> Assembly / GTF
              </div>
              <div className="text-[11px] font-mono text-slate-300 mt-1">
                GRCh38.p14 / v46
              </div>
            </div>
          </div>

          {/* Ranked Candidates Table */}
          <div className="research-card p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <SectionHeader
                title="Ranked Guide RNA Candidates"
                subtitle="Ordered by TOPSIS closeness score across 4 biophysical decision criteria"
              />
              <div className="flex flex-wrap items-center gap-2">
                <div className="relative">
                  <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Filter guides (protospacer, PAM...)"
                    className="pl-8 pr-7 py-1 rounded bg-slate-900 border border-slate-700/80 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-52 sm:w-60"
                  />
                  {searchQuery && (
                    <button
                      onClick={() => setSearchQuery('')}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                      title="Clear search"
                    >
                      <X size={12} />
                    </button>
                  )}
                </div>
                <span className="text-xs font-mono text-cyan-400 font-bold bg-cyan-950/60 px-2.5 py-1 rounded border border-cyan-800/40">
                  {filteredGuides.length} / {rankedGuides.length} Candidates
                </span>
                <button
                  onClick={handleDownloadCSV}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
                >
                  <Download size={12} />
                  <span>Export CSV</span>
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Candidate Guide</th>
                    <th>Protospacer Sequence (5&apos; &rarr; 3&apos;)</th>
                    <th>PAM</th>
                    <th>Strand</th>
                    <th>Genomic Coordinate (GRCh38)</th>
                    <th>Exon</th>
                    <th>GC Content</th>
                    <th>Predicted On-Target Efficiency</th>
                    <th>Predicted Off-Target Safety</th>
                    <th>Cancer Relevance</th>
                    <th>GC Content Optimality</th>
                    <th>TOPSIS Score</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredGuides.length === 0 ? (
                    <tr>
                      <td colSpan={14} className="text-center py-6 text-xs text-slate-400 font-mono">
                        No guide RNA candidates matched &quot;{searchQuery}&quot;. Clear search filter to view all results.
                      </td>
                    </tr>
                  ) : (
                    filteredGuides.map((g, idx) => {
                      const isRank1 = g.rank === 1;
                      return (
                        <tr
                          key={g.guide_id || g.protospacer_sequence}
                        className={isRank1 ? 'bg-cyan-950/20 border-l-2 border-l-cyan-400' : ''}
                      >
                        <td className="font-bold font-mono text-sm">
                          {isRank1 ? (
                            <span className="inline-flex items-center gap-1 text-cyan-400 font-extrabold bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/60">
                              <Sparkles size={11} /> #1 Primary
                            </span>
                          ) : g.rank === 2 ? (
                            <span className="text-amber-300 font-bold">🥈 #2</span>
                          ) : g.rank === 3 ? (
                            <span className="text-amber-500 font-bold">🥉 #3</span>
                          ) : (
                            <span className="text-slate-400 font-mono">#{g.rank}</span>
                          )}
                        </td>
                        <td className="font-mono text-slate-200 font-semibold">
                          Guide RNA {g.rank || idx + 1}
                        </td>
                        <td className="font-mono text-white font-bold tracking-wider text-xs">
                          {g.protospacer_sequence}
                        </td>
                        <td className="font-mono text-amber-400 font-extrabold">{g.pam}</td>
                        <td className="font-mono font-bold text-slate-300">{g.strand || '+'}</td>
                        <td className="font-mono text-slate-300 text-xs">
                          {g.genomic_start != null ? (
                            g.chromosome ? (
                              `chr${g.chromosome}:${g.genomic_start.toLocaleString()}–${(g.genomic_end || g.genomic_start + 23).toLocaleString()}`
                            ) : (
                              `${g.genomic_start.toLocaleString()}–${(g.genomic_end || g.genomic_start + 23).toLocaleString()}`
                            )
                          ) : (
                            'N/A'
                          )}
                        </td>
                        <td className="font-mono text-slate-300">
                          {g.exon_number != null ? `Exon ${g.exon_number}` : 'Exon 1'}
                        </td>
                        <td className="font-mono text-slate-300">
                          {(g.gc_content != null || g.gc_percentage != null)
                            ? `${(g.gc_content ?? g.gc_percentage)!.toFixed(1)}%`
                            : '50.0%'}
                        </td>
                        <td className="font-mono text-slate-200 font-semibold">
                          {g.on_target_criterion.toFixed(3)}
                        </td>
                        <td className="font-mono text-slate-200 font-semibold">
                          {g.off_target_criterion.toFixed(3)}
                        </td>
                        <td className="font-mono text-slate-300">
                          {g.cancer_relevance_criterion.toFixed(3)}
                        </td>
                        <td className="font-mono text-slate-300">
                          {g.gc_optimality_criterion.toFixed(3)}
                        </td>
                        <td className="font-mono font-extrabold text-emerald-400 text-sm">
                          {g.closeness_score.toFixed(4)}
                        </td>
                        <td>
                          <div className="flex items-center gap-1.5">
                            <button
                              onClick={() => handleOpen3DTarget(g)}
                              className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-[11px] font-bold bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 transition-all cursor-pointer"
                              title="Inspect this candidate in the 3D molecular design studio"
                            >
                              <Boxes size={12} />
                              <span>View 3D Target</span>
                            </button>
                            <button
                              onClick={() => setSelectedGuideForModal(g)}
                              className="p-1 rounded text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 transition-colors cursor-pointer"
                              title="View full candidate properties"
                            >
                              <Eye size={13} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Guide Details Modal */}
      {selectedGuideForModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="research-card max-w-2xl w-full p-6 border-slate-800 bg-slate-900 shadow-2xl space-y-5 animate-in fade-in zoom-in duration-150">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center text-cyan-400">
                  <Dna size={18} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">
                    Guide RNA {selectedGuideForModal.rank} &bull; Computational Evaluation
                  </h3>
                  <p className="text-xs text-slate-400">
                    Target: {latestRun?.gene} ({latestRun?.cancer}) &bull; Mode: {latestRun?.mode}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedGuideForModal(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>

            {/* Sequence Banner */}
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 font-mono text-xs space-y-1">
              <div className="text-[11px] text-slate-400 uppercase font-bold">Protospacer Sequence (5&apos; &rarr; 3&apos;)</div>
              <div className="text-base font-extrabold text-cyan-400 tracking-wider">
                {selectedGuideForModal.protospacer_sequence}{' '}
                <span className="text-amber-400">{selectedGuideForModal.pam}</span>
              </div>
            </div>

            {/* Criteria Breakdown Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <div className="text-[10px] text-slate-400 font-bold uppercase">On-Target Efficiency (35%)</div>
                <div className="text-base font-mono font-bold text-cyan-400 mt-1">
                  {selectedGuideForModal.on_target_criterion.toFixed(3)}
                </div>
                <div className="text-[10px] text-slate-400 mt-1">Hybrid Prediction Model</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Off-Target Safety (30%)</div>
                <div className="text-base font-mono font-bold text-emerald-400 mt-1">
                  {selectedGuideForModal.off_target_criterion.toFixed(3)}
                </div>
                <div className="text-[10px] text-slate-400 mt-1">GRCh38 CFD Specificity</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Cancer Relevance (20%)</div>
                <div className="text-base font-mono font-bold text-amber-400 mt-1">
                  {selectedGuideForModal.cancer_relevance_criterion.toFixed(3)}
                </div>
                <div className="text-[10px] text-slate-400 mt-1">TCGA Oncological Profile</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <div className="text-[10px] text-slate-400 font-bold uppercase">GC Content Optimality (15%)</div>
                <div className="text-base font-mono font-bold text-purple-400 mt-1">
                  {selectedGuideForModal.gc_optimality_criterion.toFixed(3)}
                </div>
                <div className="text-[10px] text-slate-400 mt-1">Centered at 50% GC target</div>
              </div>
            </div>

            {/* TOPSIS Math Properties */}
            <div className="p-3.5 rounded-lg bg-slate-950/40 border border-slate-800 space-y-1.5 text-xs">
              <div className="text-[11px] font-bold text-slate-300 uppercase">TOPSIS Vector Distance Metrics</div>
              <div className="grid grid-cols-3 gap-2 font-mono text-[11px] pt-1">
                <div>
                  <span className="text-slate-400">Distance to Ideal (S⁺):</span>{' '}
                  <span className="text-slate-200 font-bold">{selectedGuideForModal.distance_positive_ideal.toFixed(4)}</span>
                </div>
                <div>
                  <span className="text-slate-400">Distance to Anti-Ideal (S⁻):</span>{' '}
                  <span className="text-slate-200 font-bold">{selectedGuideForModal.distance_negative_ideal.toFixed(4)}</span>
                </div>
                <div>
                  <span className="text-slate-400">Closeness Score (Cᵢ):</span>{' '}
                  <span className="text-emerald-400 font-extrabold">{selectedGuideForModal.closeness_score.toFixed(4)}</span>
                </div>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-800">
              <button
                onClick={() => setSelectedGuideForModal(null)}
                className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-300 hover:bg-slate-800 transition-colors cursor-pointer"
              >
                Close
              </button>
              <button
                onClick={() => {
                  const g = selectedGuideForModal;
                  setSelectedGuideForModal(null);
                  handleOpen3DTarget(g);
                }}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/20 transition-all cursor-pointer"
              >
                <Boxes size={14} />
                <span>Open in 3D Design Studio</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Workflow Navigation Footer (Requirement 22: TOPSIS -> Ranked Guides -> Off-Target) */}
      <WorkflowNavigationFooter
        prevPath="/topsis-ranking"
        prevLabel="← TOPSIS Ranking"
        nextPath="/off-target"
        nextLabel="Next: Off-Target Analysis →"
      />
    </div>
  );
};
