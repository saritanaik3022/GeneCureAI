import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Activity,
  Play,
  Clock,
  AlertCircle,
  Dna,
  Target,
  ShieldCheck,
  Award,
  ArrowRight,
  Sparkles,
  Upload,
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { StatusBadge } from '../components/common/StatusBadge';
import { ModeBadge } from '../components/common/ModeBadge';

import { executePipeline } from '../services/api';
import { analysisStorage } from '../services/analysisStorage';
import { useHealth } from '../hooks/useHealth';
import { CANCER_GENE_MAP, GENE_FULL_NAMES, PipelineExecutionResponse } from '../types';
import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';
import { WorkflowNavigationFooter } from '../components/common/WorkflowNavigationFooter';

export const AnalysisPipelinePage: React.FC = () => {
  const { health } = useHealth();
  const navigate = useNavigate();
  const [selectedCancer, setSelectedCancer] = useState('Breast cancer');
  const [selectedGene, setSelectedGene] = useState('BRCA1');
  const [running, setRunning] = useState(false);
  const [navigatingToResults, setNavigatingToResults] = useState(false);
  // Always start fresh — never preload previous run into the pipeline page
  const [pipelineResult, setPipelineResult] = useState<PipelineExecutionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Custom DNA sequence states
  const [customCancer, setCustomCancer] = useState('Breast cancer');
  const [customName, setCustomName] = useState('');
  const [customSequence, setCustomSequence] = useState('');

  const handleRunPipeline = async () => {
    setRunning(true);
    setError(null);
    setNavigatingToResults(false);
    setPipelineResult(null); // clear any previous result
    try {
      const res = await executePipeline({
        gene_symbol: selectedGene,
        cancer_type: selectedCancer,
        execution_mode: health?.execution_mode || 'REAL_MODE',
        top_n: 10,
      });
      setPipelineResult(res);
      if (res.status === 'COMPLETED') {
        const savedRun = analysisStorage.saveRun(res, selectedCancer);
        setNavigatingToResults(true);
        // Navigate to Design Studio with the top guide + autoStart so simulation runs immediately
        const topGuide = res.ranked_guides?.[0] || null;
        setTimeout(() => {
          navigate('/design-studio', {
            state: {
              selectedGuide: topGuide,
              geneSymbol: selectedGene,
              cancerType: selectedCancer,
              autoStart: true,
              runId: savedRun.runId,
            },
          });
        }, 800);
      }
    } catch (err: any) {
      setError(err?.message || 'Pipeline execution failed.');
    } finally {
      setRunning(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      if (content) {
        setCustomSequence(content);
        const firstLine = content.split('\n')[0];
        if (firstLine.startsWith('>') && !customName) {
          const headerName = firstLine.slice(1).split(/[\s|]/)[0].trim();
          if (headerName) setCustomName(headerName);
        }
      }
    };
    reader.readAsText(file);
  };

  const handleRunCustomPipeline = async () => {
    const raw = customSequence.trim();
    if (!raw) {
      setError('Please provide a DNA sequence or FASTA format.');
      return;
    }
    const lines = raw.split('\n');
    const seqLines = lines.filter((l) => !l.trim().startsWith('>'));
    const cleanDna = seqLines.join('').replace(/[^A-Za-z]/g, '').toUpperCase();

    if (cleanDna.length < 23) {
      setError('DNA sequence must be at least 23 nucleotides long for SpCas9 protospacer (20nt) + PAM (3nt) scanning.');
      return;
    }

    setRunning(true);
    setError(null);
    setNavigatingToResults(false);
    setPipelineResult(null);

    const displayName = customName.trim() || 'Custom-DNA';

    try {
      const res = await executePipeline({
        gene_symbol: displayName,
        cancer_type: customCancer,
        custom_sequence: cleanDna,
        execution_mode: health?.execution_mode || 'REAL_MODE',
        top_n: 10,
      });

      setPipelineResult(res);
      if (res.status === 'COMPLETED') {
        const savedRun = analysisStorage.saveRun(res, customCancer, cleanDna);
        setNavigatingToResults(true);
        const topGuide = res.ranked_guides?.[0] || null;
        setTimeout(() => {
          navigate('/design-studio', {
            state: {
              selectedGuide: topGuide,
              geneSymbol: displayName,
              cancerType: customCancer,
              customSequence: cleanDna,
              autoStart: true,
              runId: savedRun.runId,
            },
          });
        }, 800);
      } else {
        setError(res.stage_summaries?.find((s) => s.status === 'FAILED')?.summary || 'Custom sequence analysis failed.');
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to execute custom DNA sequence pipeline.');
    } finally {
      setRunning(false);
    }
  };

  const defaultStages = [
    {
      num: 1,
      name: 'Cancer Gene Selection & CDS Ingestion',
      icon: Target,
      desc: 'Retrieves canonical transcript CDS sequence and genomic coordinates from NCBI/Ensembl.',
    },
    {
      num: 2,
      name: 'Guide RNA Identification (SpCas9)',
      icon: Dna,
      desc: 'Scans dual DNA strands for 5\'-NGG PAM motifs; extracts 20-nt protospacers with 30-nt context.',
    },
    {
      num: 3,
      name: 'On-Target Efficiency ML Prediction',
      icon: Activity,
      desc: 'Evaluates dual PyTorch 1D-CNN sequence representations and XGBoost 105-feature vector ensemble.',
    },
    {
      num: 4,
      name: 'Off-Target Specificity & CFD Analysis',
      icon: ShieldCheck,
      desc: 'Executes seed-and-extend GRCh38 alignment with Cutting Frequency Determination scoring.',
    },
    {
      num: 5,
      name: 'TOPSIS Multi-Criteria Ranking',
      icon: Award,
      desc: 'Performs vector normalization, ideal distance calculation, and closeness scoring (35/30/20/15).',
    },
  ];

  return (
    <div className="relative w-full px-4 sm:px-6 lg:px-8 py-6 space-y-6 fade-in">
      <ScientificMolecularBackground intensity={0.55} />
      {/* Header */}
      <div className="research-card p-6 border-slate-800 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950/90">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                Pipeline Orchestration
              </span>
              <ModeBadge mode={health?.execution_mode || 'REAL_MODE'} />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <Activity className="w-7 h-7 text-cyan-400" />
              <span>Analysis Pipeline Execution</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Automated multi-stage execution orchestrating gene sequence extraction, gRNA discovery, on-target ML scoring, GRCh38 off-target search, and TOPSIS ranking.
            </p>
          </div>

          <button
            onClick={handleRunPipeline}
            disabled={running}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-slate-950 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
          >
            {running ? <Clock className="animate-spin" size={14} /> : <Play size={14} fill="currentColor" />}
            <span>{running ? 'Executing Pipeline...' : 'Execute Full Pipeline'}</span>
          </button>
        </div>
      </div>



      {/* Gene Selection / Execution Config */}
      <div className="research-card p-5 space-y-4">
        <SectionHeader
          title="Analysis Configuration (Curated Cancer Genes)"
          subtitle="Select target cancer entity and oncogene / tumor suppressor for in-silico guide evaluation"
        />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Target Cancer Type
            </label>
            <select
              value={selectedCancer}
              onChange={(e) => {
                const ct = e.target.value;
                setSelectedCancer(ct);
                const gList = CANCER_GENE_MAP[ct] || [];
                if (gList.length > 0) setSelectedGene(gList[0]);
              }}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            >
              <option value="Breast cancer">Breast cancer</option>
              <option value="Lung cancer">Lung cancer</option>
              <option value="Liver cancer">Liver cancer</option>
            </select>
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Target Gene Symbol
            </label>
            <select
              value={selectedGene}
              onChange={(e) => setSelectedGene(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
            >
              {(CANCER_GENE_MAP[selectedCancer] || []).map((sym) => (
                <option key={sym} value={sym}>
                  {GENE_FULL_NAMES[sym] || sym}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Reference Genome Assembly
            </label>
            <input
              type="text"
              readOnly
              value="GRCh38.p14 (Primary Assembly)"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-400 font-mono"
            />
          </div>
        </div>
      </div>

      {/* ------------------------------------------------------------ */}
      {/* CUSTOM / NEW DNA SEQUENCE ANALYSIS */}
      {/* ------------------------------------------------------------ */}
      <div className="research-card p-6 space-y-5 border-cyan-900/40 bg-gradient-to-br from-slate-900/90 via-slate-950/90 to-cyan-950/20">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-800/80 pb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-800/50">
                Custom Input Mode
              </span>
              <span className="text-[10px] font-mono text-slate-400">FASTA / Raw DNA Sequence</span>
            </div>
            <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <Dna className="w-5 h-5 text-cyan-400" />
              <span>Analyze a New DNA Sequence</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Run computational guide-RNA analysis on a newly provided DNA sequence.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <label className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-cyan-300 hover:text-white bg-cyan-950/60 hover:bg-cyan-900/80 border border-cyan-800/60 transition-colors cursor-pointer">
              <Upload size={13} />
              <span>Upload FASTA</span>
              <input
                type="file"
                accept=".fasta,.fa,.txt,.fna"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Target Cancer Type
            </label>
            <select
              value={customCancer}
              onChange={(e) => setCustomCancer(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            >
              <option value="Breast cancer">Breast Cancer</option>
              <option value="Lung cancer">Lung Cancer</option>
              <option value="Liver cancer">Liver Cancer</option>
              <option value="Other / Not Specified">Other / Not Specified</option>
            </select>
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Target Gene or Sequence Name
            </label>
            <input
              type="text"
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              placeholder="Target Gene or Sequence Name"
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Reference Genome Assembly
            </label>
            <input
              type="text"
              readOnly
              value="GRCh38.p14 (Default)"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-400 font-mono"
            />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              DNA Sequence Input
            </label>
            {customSequence.length > 0 && (
              <span className="text-[10px] font-mono text-cyan-400">
                {customSequence.replace(/^>.*$/m, '').replace(/[^A-Za-z]/g, '').length} bp detected
              </span>
            )}
          </div>
          <textarea
            value={customSequence}
            onChange={(e) => setCustomSequence(e.target.value)}
            placeholder="Paste a DNA sequence (A, C, G, T) or FASTA sequence..."
            rows={5}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500 placeholder:text-slate-600 resize-y"
          />
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
          <div className="text-[11px] text-slate-500 font-mono">
            Accepts raw DNA (A, C, G, T) or standard FASTA format. Requires &ge; 23 bp for dual-strand SpCas9 PAM scanning.
          </div>

          <button
            onClick={handleRunCustomPipeline}
            disabled={running || customSequence.trim().length < 23}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-slate-950 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
          >
            {running ? <Clock className="animate-spin" size={14} /> : <Play size={14} fill="currentColor" />}
            <span>ANALYZE NEW DNA SEQUENCE →</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-xs text-red-300 flex items-center gap-2">
          <AlertCircle size={16} className="text-red-400 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* 5 Pipeline Stages Execution Monitor */}
      <div className="research-card p-5 space-y-4">
        <SectionHeader
          title="Five-Stage Execution Progress"
          subtitle="Real-time computational execution stages and duration breakdown"
          badge={
            pipelineResult && (
              <StatusBadge status={pipelineResult.status} />
            )
          }
        />

        <div className="space-y-3">
          {defaultStages.map((st) => {
            const Icon = st.icon;
            const liveStage = pipelineResult?.stage_summaries.find((s) => s.stage_number === st.num);
            const isDone = !!liveStage;

            return (
              <div
                key={st.num}
                className={`p-4 rounded-xl border transition-all ${
                  isDone
                    ? 'bg-slate-900/60 border-emerald-500/40'
                    : 'bg-slate-900/20 border-slate-800/80'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                        isDone ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      <Icon size={16} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-cyan-400">Stage 0{st.num}</span>
                        <h4 className="text-xs font-bold text-white">{st.name}</h4>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-0.5">{st.desc}</p>
                      {liveStage && (
                        <p className="text-[11px] font-mono text-slate-300 mt-2 bg-slate-950/80 p-2 rounded border border-slate-800">
                          {liveStage.summary}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-1 flex-shrink-0">
                    <StatusBadge status={liveStage ? liveStage.status : running ? 'RUNNING' : 'PENDING'} />
                    {liveStage && (
                      <span className="text-[10px] font-mono text-slate-400">
                        {liveStage.duration_ms} ms
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Final Ranked Guides Output if pipeline completed */}
      {pipelineResult && (
        <div className="space-y-4">
          {/* Navigation Banner */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-950/80 via-slate-900 to-cyan-950/80 border border-emerald-500/50 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-lg shadow-emerald-950/30">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
                <Sparkles size={18} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>Pipeline Analysis Completed</span>
                  <span className="text-[10px] font-mono text-emerald-300 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                    {pipelineResult.total_guides_scanned} Guides Scanned
                  </span>
                </h3>
                <p className="text-xs text-slate-300 mt-0.5">
                  {navigatingToResults
                    ? 'Starting 3D computational simulation. Automatically navigating to Design Studio...'
                    : 'Candidates scored across all 4 criteria and ranked using TOPSIS. Starting 3D simulation...'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <button
                onClick={() => navigate('/design-studio', { state: { selectedGuide: pipelineResult.ranked_guides?.[0], geneSymbol: pipelineResult.gene_symbol, cancerType: selectedCancer, autoStart: true } })}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/20 transition-all cursor-pointer"
              >
                <span>Open 3D Simulation</span>
                <ArrowRight size={14} />
              </button>
              <button
                onClick={() => navigate('/ranked-guides')}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors cursor-pointer"
              >
                <span>View Ranked Guides</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>

          <div className="research-card p-5 space-y-4">
            <SectionHeader
              title="Ranked Guide RNAs (Top Candidates)"
              subtitle={`Run ID: ${pipelineResult.run_id} | Total Guides Scanned: ${pipelineResult.total_guides_scanned} | Execution Time: ${pipelineResult.total_execution_time_ms} ms`}
              action={<ModeBadge mode={pipelineResult.execution_mode} />}
            />

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
                    <th>TOPSIS Score</th>
                  </tr>
                </thead>
                <tbody>
                  {pipelineResult.ranked_guides.map((g) => (
                    <tr key={g.guide_id || g.protospacer_sequence}>
                      <td className="font-bold text-cyan-400 font-mono">
                        {g.rank === 1 ? '🥇 #1' : g.rank === 2 ? '🥈 #2' : `#${g.rank}`}
                      </td>
                      <td className="font-mono text-slate-200 font-semibold">Guide RNA {g.rank}</td>
                      <td className="font-mono text-white font-bold tracking-wider">{g.protospacer_sequence}</td>
                      <td className="font-mono text-amber-400 font-bold">{g.pam}</td>
                      <td className="font-mono text-slate-300">{g.on_target_criterion.toFixed(3)}</td>
                      <td className="font-mono text-slate-300">{g.off_target_criterion.toFixed(3)}</td>
                      <td className="font-mono text-slate-300">{g.cancer_relevance_criterion.toFixed(3)}</td>
                      <td className="font-mono text-slate-300">{g.gc_optimality_criterion.toFixed(3)}</td>
                      <td className="font-mono font-bold text-emerald-400">{g.closeness_score.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Workflow Navigation Footer */}
      <WorkflowNavigationFooter
        prevPath="/"
        prevLabel="← Dashboard"
        nextPath="/design-studio"
        nextLabel="Next: 3D Simulation →"
        onNext={() => {
          if (pipelineResult && pipelineResult.ranked_guides.length > 0) {
            navigate('/design-studio', {
              state: {
                selectedGuide: pipelineResult.ranked_guides[0],
                geneSymbol: selectedGene,
                cancerType: selectedCancer,
                autoStart: true,
              },
            });
          }
        }}
      />
    </div>
  );
};
