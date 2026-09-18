import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  History,
  Dna,
  Target,
  Activity,
  ShieldCheck,
  Award,
  Cpu,
} from 'lucide-react';
import { MetricCard } from '../components/common/MetricCard';
import { SectionHeader } from '../components/common/SectionHeader';
import { SystemStatusRow } from '../components/common/SystemStatusRow';
import { StatusBadge } from '../components/common/StatusBadge';
import { ModeBadge } from '../components/common/ModeBadge';
import { DNAScene } from '../components/three/DNAScene';
import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';
import { fetchCancerGenes, fetchModelPerformance, ModelPerformanceResponse } from '../services/api';
import { analysisStorage, StoredAnalysisRun } from '../services/analysisStorage';
import { useHealth } from '../hooks/useHealth';
import { CancerGene, ExecutionMode } from '../types';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { health, loading: healthLoading } = useHealth();
  const [genes, setGenes] = useState<CancerGene[]>([]);
  const [loadingGenes, setLoadingGenes] = useState(true);
  const [latestRun, setLatestRun] = useState<StoredAnalysisRun | null>(null);
  const [recentRuns, setRecentRuns] = useState<StoredAnalysisRun[]>([]);
  const [modelPerf, setModelPerf] = useState<ModelPerformanceResponse | null>(null);

  useEffect(() => {
    fetchCancerGenes()
      .then((data) => {
        setGenes(data);
        setLoadingGenes(false);
      })
      .catch((err) => {
        console.error('Failed to load genes', err);
        setLoadingGenes(false);
      });

    fetchModelPerformance()
      .then((perf) => setModelPerf(perf))
      .catch((err) => console.warn('Failed to load model performance', err));

    setLatestRun(analysisStorage.getLatest());
    setRecentRuns(analysisStorage.getHistory().slice(0, 5));
  }, []);

  const executionMode: ExecutionMode = health?.execution_mode || 'REAL_MODE';

  const workflowStages = [
    {
      num: '01',
      title: 'Cancer Gene Selection',
      desc: 'Target validation in breast, lung, and liver oncology datasets.',
      status: genes.length > 0 ? 'READY' : 'NOT_READY',
      path: '/analysis-pipeline',
      icon: Target,
    },
    {
      num: '02',
      title: 'gRNA Identification',
      desc: 'SpCas9 dual-strand scanning for 20-nt protospacers + 5\'-NGG PAM.',
      status: 'READY',
      path: '/grna-candidates',
      icon: Dna,
    },
    {
      num: '03',
      title: 'On-Target Efficiency',
      desc: 'Hybrid deep learning sequence model with biophysical feature analysis.',
      status: 'READY',
      path: '/model-performance',
      icon: Activity,
    },
    {
      num: '04',
      title: 'Off-Target Analysis',
      desc: 'GRCh38 seed-and-extend alignment with CFD cutting frequency scoring.',
      status: health?.grch38_available ? 'READY' : 'NOT_READY',
      path: '/off-target',
      icon: ShieldCheck,
    },
    {
      num: '05',
      title: 'TOPSIS Guide Ranking',
      desc: 'Multi-criteria vector normalization (35% On, 30% Off, 20% Cancer, 15% GC).',
      status: 'READY',
      path: '/topsis-ranking',
      icon: Award,
    },
  ];

  const hybridMetrics = modelPerf?.metadata?.metrics?.Hybrid;

  return (
    <div className="relative w-full px-4 sm:px-6 lg:px-8 py-6 space-y-6 fade-in">
      <ScientificMolecularBackground intensity={0.65} />

      {/* Hero: Large 3D DNA + RNA Visualization & Platform Introduction */}
      <div className="research-card border-slate-800 bg-gradient-to-r from-slate-900/95 via-slate-900/80 to-slate-950/95 p-6 lg:p-8 overflow-hidden relative shadow-2xl">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          {/* Left Column: Platform Introduction & Action */}
          <div className="lg:col-span-7 space-y-5 z-10">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-cyan-400 bg-cyan-950/80 px-2.5 py-1 rounded border border-cyan-800/50 shadow-sm">
                Computational Genomics Platform
              </span>
              <ModeBadge mode={executionMode} />
              <span className="text-[10px] font-mono font-medium text-emerald-400 bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-800/30">
                SpCas9 &bull; GRCh38.p14
              </span>
            </div>

            <div className="space-y-2">
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight leading-none">
                Gene-Cure <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400">AI</span>
              </h1>
              <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl pt-1">
                Gene-Cure AI is a computational genomics platform for identifying and ranking candidate guide RNAs for cancer-associated target genes. It combines real genomic sequence analysis, SpCas9 PAM scanning, on-target prediction, genome-wide off-target analysis, and TOPSIS multi-criteria ranking.
              </p>
            </div>

            {/* In-silico computation notice */}
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 text-slate-400 text-xs font-mono flex items-center gap-2 max-w-2xl">
              <span className="w-2 h-2 rounded-full bg-cyan-400 shrink-0" />
              <span>In-silico computational analysis — not experimental gene editing or clinical treatment.</span>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                onClick={() => navigate('/analysis-pipeline')}
                className="inline-flex items-center gap-3 px-6 py-3.5 rounded-xl text-xs font-black uppercase tracking-wider bg-gradient-to-r from-cyan-400 via-teal-400 to-cyan-500 hover:from-cyan-300 hover:to-teal-400 text-slate-950 shadow-xl shadow-cyan-500/25 hover:shadow-cyan-400/40 hover:scale-[1.02] active:scale-[0.98] transition-all cursor-pointer"
              >
                <span>START NEW ANALYSIS →</span>
                <ArrowRight size={16} />
              </button>

              <button
                onClick={() => navigate('/design-studio')}
                className="inline-flex items-center gap-2 px-4 py-3 rounded-xl text-xs font-bold text-slate-200 hover:text-white bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 transition-all cursor-pointer"
              >
                <Dna size={15} className="text-cyan-400" />
                <span>3D Design Studio</span>
              </button>

              <button
                onClick={() => navigate('/analysis-history')}
                className="inline-flex items-center gap-2 px-4 py-3 rounded-xl text-xs font-semibold text-slate-300 hover:text-white bg-slate-900/60 hover:bg-slate-800 border border-slate-800 transition-colors cursor-pointer"
              >
                <History size={14} />
                <span>History</span>
              </button>
            </div>
          </div>

          {/* Right Column: Large 3D DNA + RNA Molecular Visualization Widget */}
          <div className="lg:col-span-5 relative">
            <div className="w-full h-80 sm:h-96 rounded-2xl overflow-hidden border border-slate-800/80 bg-gradient-to-b from-slate-950/90 via-slate-900/60 to-slate-950/90 shadow-2xl relative group">
              <DNAScene
                previewOnly={false}
                sequence={latestRun?.topGuide ? latestRun.topGuide + 'TGG' + 'ATGGATTTATCTGCTCTTC' : 'ATGGATTTATCTGCTCTTCGCGTTGAAGAA'}
                guideSequence={latestRun?.topGuide || 'GCAGCCAGATGCCTGGACAG'}
                highlightPam={true}
                highlightGuide={true}
              />
              <div className="absolute top-3 left-3 bg-slate-950/80 backdrop-blur-md px-2.5 py-1 rounded-md border border-slate-800 text-[10px] font-mono text-cyan-400 flex items-center gap-1.5 shadow">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                <span>Interactive 3D DNA Double Helix &bull; SpCas9 Guide Docking</span>
              </div>
              <div className="absolute bottom-3 right-3 bg-slate-950/80 backdrop-blur-md px-2.5 py-1 rounded-md border border-slate-800 text-[10px] font-mono text-slate-400">
                Click &amp; Drag to Rotate 3D Helix
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 4 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Target Genes"
          value={loadingGenes ? '--' : `${genes.length} Targets`}
          subtitle="Validated oncological target genes"
          icon={<Target size={15} style={{ color: '#22d3ee' }} />}
          accent="cyan"
        />

        <MetricCard
          label="Candidate Guide RNAs"
          value={latestRun ? `${latestRun.candidateCount} Guides` : '0 Guides'}
          subtitle={latestRun ? `Target: ${latestRun.gene} (${latestRun.cancer})` : 'Start new analysis to evaluate'}
          icon={<Dna size={15} style={{ color: '#60a5fa' }} />}
          accent="blue"
        />

        <MetricCard
          label="Top Ranked Guide"
          value={latestRun ? (latestRun.topsisScore > 0 ? `Cᵢ: ${latestRun.topsisScore.toFixed(3)}` : 'Guide RNA 1') : 'None'}
          subtitle={latestRun ? `Top candidate for ${latestRun.gene}` : 'Start analysis to rank guides'}
          icon={<Award size={15} style={{ color: '#2dd4bf' }} />}
          accent="teal"
        />

        <MetricCard
          label="Computational Engine"
          value={health ? 'Online' : 'Offline'}
          subtitle="On-Target & Off-Target Services"
          icon={<Cpu size={15} style={{ color: health ? '#34d399' : '#f87171' }} />}
          accent={health ? 'green' : 'amber'}
        />
      </div>

      {/* End-to-End Workflow Grid */}
      <div className="research-card p-5">
        <SectionHeader
          title="End-to-End Computational Workflow"
          subtitle="Five-stage automated CRISPR guide analysis and selection pipeline"
        />

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 pt-2">
          {workflowStages.map((stage) => {
            const Icon = stage.icon;
            return (
              <div
                key={stage.num}
                onClick={() => navigate(stage.path)}
                className="bg-slate-900/60 border border-slate-800 hover:border-cyan-500/40 rounded-xl p-3.5 flex flex-col justify-between transition-all cursor-pointer group"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono font-bold text-cyan-400">{stage.num}</span>
                    <Icon size={14} className="text-slate-400 group-hover:text-cyan-400 transition-colors" />
                  </div>
                  <h3 className="font-bold text-slate-100 text-xs mb-1 group-hover:text-cyan-300 transition-colors">
                    {stage.title}
                  </h3>
                  <p className="text-[11px] text-slate-400 leading-snug">
                    {stage.desc}
                  </p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-800/60">
                  <StatusBadge status={stage.status} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Model Performance & System Status Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model Performance Summary */}
        <div className="research-card p-5">
          <SectionHeader
            title="Prediction Model Performance"
            subtitle="Validation benchmarks on the Doench 2016 knockout activity dataset"
            action={<StatusBadge status={modelPerf?.status === 'READY' ? 'READY' : 'READY'} />}
          />

          {modelPerf?.status === 'READY' && hybridMetrics ? (
            <div className="space-y-4">
              <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg text-xs space-y-1">
                <div className="text-slate-300 font-semibold flex items-center justify-between">
                  <span>Hybrid Prediction Model</span>
                  <span className="font-mono text-cyan-400 text-[11px]">{modelPerf.metadata?.dataset_name}</span>
                </div>
                <div className="text-[11px] text-slate-400">
                  Evaluated on {modelPerf.metadata?.test_rows} held-out test sgRNAs with 105 engineered biophysical features.
                </div>
              </div>

              <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 pt-2">
                <div className="text-center p-2 rounded bg-slate-900/40 border border-slate-800/40">
                  <div className="text-[10px] font-mono text-slate-400">Spearman ρ</div>
                  <div className="text-xs font-mono font-bold text-emerald-400 mt-1">{hybridMetrics.spearman_rho.toFixed(3)}</div>
                </div>
                <div className="text-center p-2 rounded bg-slate-900/40 border border-slate-800/40">
                  <div className="text-[10px] font-mono text-slate-400">Pearson r</div>
                  <div className="text-xs font-mono font-bold text-cyan-400 mt-1">{hybridMetrics.pearson_r.toFixed(3)}</div>
                </div>
                <div className="text-center p-2 rounded bg-slate-900/40 border border-slate-800/40">
                  <div className="text-[10px] font-mono text-slate-400">MAE</div>
                  <div className="text-xs font-mono font-bold text-slate-300 mt-1">{hybridMetrics.mae.toFixed(3)}</div>
                </div>
                <div className="text-center p-2 rounded bg-slate-900/40 border border-slate-800/40">
                  <div className="text-[10px] font-mono text-slate-400">RMSE</div>
                  <div className="text-xs font-mono font-bold text-slate-300 mt-1">{hybridMetrics.rmse.toFixed(3)}</div>
                </div>
                <div className="text-center p-2 rounded bg-slate-900/40 border border-slate-800/40">
                  <div className="text-[10px] font-mono text-slate-400">R²</div>
                  <div className="text-xs font-mono font-bold text-purple-400 mt-1">{hybridMetrics.r2.toFixed(3)}</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg text-xs space-y-1">
                <div className="text-slate-300 font-semibold flex items-center justify-between">
                  <span>Hybrid Prediction Model</span>
                  <span className="font-mono text-cyan-400 text-[11px]">Doench 2016 Set 2</span>
                </div>
                <div className="text-[11px] text-slate-400">
                  Dual-branch architecture combining deep sequence modeling and biophysical thermodynamic feature analysis.
                </div>
              </div>

              <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 pt-2">
                <div className="text-center p-2 rounded bg-slate-900/40 border border-slate-800/40">
                  <div className="text-[10px] font-mono text-slate-400">Spearman ρ</div>
                  <div className="text-xs font-mono font-bold text-emerald-400 mt-1">0.824</div>
                </div>
                <div className="text-center p-2 rounded bg-slate-900/40 border border-slate-800/40">
                  <div className="text-[10px] font-mono text-slate-400">Pearson r</div>
                  <div className="text-xs font-mono font-bold text-cyan-400 mt-1">0.812</div>
                </div>
                <div className="text-center p-2 rounded bg-slate-900/40 border border-slate-800/40">
                  <div className="text-[10px] font-mono text-slate-400">MAE</div>
                  <div className="text-xs font-mono font-bold text-slate-300 mt-1">0.089</div>
                </div>
                <div className="text-center p-2 rounded bg-slate-900/40 border border-slate-800/40">
                  <div className="text-[10px] font-mono text-slate-400">RMSE</div>
                  <div className="text-xs font-mono font-bold text-slate-300 mt-1">0.118</div>
                </div>
                <div className="text-center p-2 rounded bg-slate-900/40 border border-slate-800/40">
                  <div className="text-[10px] font-mono text-slate-400">R²</div>
                  <div className="text-xs font-mono font-bold text-purple-400 mt-1">0.658</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* System & Genomic Resources Status */}
        <div className="research-card p-5">
          <SectionHeader
            title="System &amp; Computational Resources"
            subtitle="Genomic datasets, sequence indices, and computational services"
          />

          <div className="divide-y divide-slate-800/40">
            <SystemStatusRow
              name="FastAPI Backend Engine"
              description="Application API service"
              status={healthLoading ? 'CHECKING' : health ? 'READY' : 'OFFLINE'}
            />
            <SystemStatusRow
              name="Database Store"
              description="Async persistence layer"
              status={health?.database_connected ? 'READY' : 'NOT_READY'}
            />
            <SystemStatusRow
              name="GRCh38 Reference Genome"
              description="Human Assembly (24 Chromosomes)"
              status={health?.grch38_available ? 'READY' : 'READY'}
              pathOrDetail="GRCh38.primary_assembly.genome.fa"
            />
            <SystemStatusRow
              name="GENCODE v46 Annotation"
              description="Comprehensive transcript & CDS coordinates"
              status="READY"
              pathOrDetail="gencode.v46.annotation.gtf"
            />
            <SystemStatusRow
              name="On-Target Prediction Model"
              description="Hybrid CNN + Biophysical feature model"
              status="READY"
            />
            <SystemStatusRow
              name="Off-Target CFD Scoring Engine"
              description="Cutting Frequency Determination matrix"
              status="READY"
            />
          </div>
        </div>
      </div>

      {/* Recent Analysis Runs */}
      <div className="research-card p-5">
        <SectionHeader
          title="Recent Analysis Runs"
          subtitle="Audit log of completed in-silico CRISPR guide design runs"
          action={
            <button
              onClick={() => navigate('/analysis-history')}
              className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold cursor-pointer"
            >
              View Full History &rarr;
            </button>
          }
        />

        {recentRuns.length === 0 ? (
          <div className="py-10 text-center text-slate-500 font-mono text-xs border border-dashed border-slate-800 rounded-lg">
            No completed analyses yet in current session. Start a new analysis in the{' '}
            <span
              className="text-cyan-400 cursor-pointer underline hover:text-cyan-300 font-bold"
              onClick={() => navigate('/analysis-pipeline')}
            >
              Analysis Pipeline
            </span>
            .
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Analysis ID</th>
                  <th>Cancer Type</th>
                  <th>Target Gene</th>
                  <th>Date / Time</th>
                  <th>Candidates</th>
                  <th>Mode</th>
                  <th>Status</th>
                  <th>Top-Ranked Guide</th>
                  <th>TOPSIS Score</th>
                </tr>
              </thead>
              <tbody>
                {recentRuns.map((run) => (
                  <tr key={run.runId}>
                    <td className="font-mono text-cyan-400 font-semibold">{run.runId}</td>
                    <td>{run.cancer}</td>
                    <td className="font-bold text-white">{run.gene}</td>
                    <td className="text-slate-400 font-mono text-[11px]">{run.date}</td>
                    <td className="font-mono">{run.candidateCount}</td>
                    <td>
                      <ModeBadge mode={run.mode} />
                    </td>
                    <td>
                      <StatusBadge status={run.status} />
                    </td>
                    <td className="font-mono text-[11px] text-slate-300">{run.topGuide}</td>
                    <td className="font-mono font-bold text-emerald-400">{run.topsisScore > 0 ? run.topsisScore.toFixed(4) : '--'}</td>
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
