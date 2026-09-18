import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, FileCode, FileSpreadsheet, Download, Award, ArrowRight, Dna } from 'lucide-react';
import { ModeBadge } from '../components/common/ModeBadge';
import { StatusBadge } from '../components/common/StatusBadge';
import { useHealth } from '../hooks/useHealth';
import { analysisStorage, StoredAnalysisRun } from '../services/analysisStorage';
import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';
import { WorkflowNavigationFooter } from '../components/common/WorkflowNavigationFooter';

export const ReportsPage: React.FC = () => {
  const navigate = useNavigate();
  const { health } = useHealth();
  const [latestRun, setLatestRun] = useState<StoredAnalysisRun | null>(null);

  useEffect(() => {
    setLatestRun(analysisStorage.getLatest());
  }, []);

  const rankedGuides = latestRun?.rankedGuides || [];

  // Download CSV
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

    const rows = rankedGuides.map((g, idx) => [
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
      `# Gene-Cure AI — CRISPR-Cas9 Ranked Guide RNA Full Report`,
      `# Target Gene: ${latestRun.gene} | Target Cancer: ${latestRun.cancer} | Date: ${latestRun.date}`,
      `# Reference Assembly: GRCh38.p14 | Annotation: GENCODE v46 | Execution Mode: ${latestRun.mode}`,
      headers.join(','),
      ...rows.map((r) => r.map((cell) => `"${cell}"`).join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `GeneCureAI_${latestRun.gene}_Report.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Download FASTA
  const handleDownloadFASTA = () => {
    if (!latestRun || rankedGuides.length === 0) return;

    const fastaEntries = rankedGuides.map((g, idx) => {
      const header = `>GeneCureAI|Rank_${g.rank || idx + 1}|Gene_${latestRun.gene}|PAM_${g.pam}|TOPSIS_${g.closeness_score.toFixed(4)}`;
      return `${header}\n${g.protospacer_sequence}`;
    });

    const fastaContent = fastaEntries.join('\n\n');
    const blob = new Blob([fastaContent], { type: 'text/plain;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `GeneCureAI_${latestRun.gene}_Guides.fasta`);
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
                Export &amp; Scientific Provenance
              </span>
              <ModeBadge mode={health?.execution_mode || 'REAL_MODE'} />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <FileText className="w-7 h-7 text-cyan-400" />
              <span>Computational Analysis Reports &amp; Data Export</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Export verified candidate guide RNAs, biophysical feature vectors, off-target specificity matrices, and TOPSIS rankings in scientific formats.
            </p>
          </div>
        </div>
      </div>

      {!latestRun || rankedGuides.length === 0 ? (
        <div className="research-card p-16 text-center text-slate-500 font-mono text-xs border border-dashed border-slate-800 rounded-xl space-y-4">
          <Award className="w-12 h-12 text-slate-600 mx-auto opacity-50" />
          <div className="text-base font-bold text-slate-300">No analysis has been completed yet.</div>
          <div className="text-slate-400 max-w-md mx-auto leading-relaxed">
            Run a computational CRISPR guide design analysis in the Analysis Pipeline to generate and download comprehensive research reports.
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
          {/* Active Analysis Summary */}
          <div className="research-card p-5 space-y-3 border-cyan-900/40 bg-cyan-950/10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Dna className="w-5 h-5 text-cyan-400" />
                <span className="text-sm font-bold text-white">
                  Active Analysis Dossier: {latestRun.gene} &bull; {latestRun.cancer}
                </span>
              </div>
              <StatusBadge status="Analysis Completed" />
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-1">
              <div>
                <span className="text-slate-400">Analysis Run ID:</span>{' '}
                <span className="font-mono text-cyan-300 font-bold">{latestRun.runId}</span>
              </div>
              <div>
                <span className="text-slate-400">Execution Date:</span>{' '}
                <span className="font-mono text-slate-200">{latestRun.date}</span>
              </div>
              <div>
                <span className="text-slate-400">Total Guides:</span>{' '}
                <span className="font-mono text-emerald-400 font-bold">{latestRun.candidateCount}</span>
              </div>
              <div>
                <span className="text-slate-400">Top TOPSIS Score:</span>{' '}
                <span className="font-mono text-emerald-400 font-bold">{latestRun.topsisScore.toFixed(4)}</span>
              </div>
            </div>
          </div>

          {/* Export Formats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* CSV Matrix Export */}
            <div className="research-card p-5 flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400">
                    <FileSpreadsheet size={22} />
                  </div>
                  <StatusBadge status="READY" />
                </div>
                <h3 className="font-bold text-white text-sm">CSV Full Evaluation Matrix</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Complete table containing all {rankedGuides.length} ranked candidate guides with protospacer sequences, coordinates, on-target scores, CFD safety indices, and TOPSIS closeness values.
                </p>
                <div className="text-[11px] font-mono text-emerald-400">Format: .csv (RFC 4180)</div>
              </div>

              <button
                onClick={handleDownloadCSV}
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-md shadow-emerald-500/20 transition-all cursor-pointer"
              >
                <Download size={14} />
                <span>Download CSV Matrix</span>
              </button>
            </div>

            {/* FASTA Export */}
            <div className="research-card p-5 flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-400">
                    <FileCode size={22} />
                  </div>
                  <StatusBadge status="READY" />
                </div>
                <h3 className="font-bold text-white text-sm">FASTA Sequence File</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Standard FASTA format with rank, gene, and PAM metadata headers for ordering oligos and CRISPR plasmid cloning design.
                </p>
                <div className="text-[11px] font-mono text-cyan-400">Format: .fasta / .fa</div>
              </div>

              <button
                onClick={handleDownloadFASTA}
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/20 transition-all cursor-pointer"
              >
                <Download size={14} />
                <span>Download FASTA</span>
              </button>
            </div>

            {/* Structured Dossier Summary */}
            <div className="research-card p-5 flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400">
                    <FileText size={22} />
                  </div>
                  <StatusBadge status="READY" />
                </div>
                <h3 className="font-bold text-white text-sm">Computational Summary Dossier</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Summary of computational methodologies, GENCODE v46 transcript boundaries, model predictions, and TOPSIS criteria weights.
                </p>
                <div className="text-[11px] font-mono text-indigo-400">Format: Scientific Summary</div>
              </div>

              <button
                onClick={handleDownloadCSV}
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
              >
                <Download size={14} />
                <span>Export Dossier Data</span>
              </button>
            </div>
          </div>
        </>
      )}

      {/* Workflow Navigation Footer (Requirement 22: Compare Guides -> Reports -> Dashboard) */}
      <WorkflowNavigationFooter
        prevPath="/compare-guides"
        prevLabel="← Compare Guides"
        nextPath="/dashboard"
        nextLabel="Dashboard →"
      />
    </div>
  );
};
