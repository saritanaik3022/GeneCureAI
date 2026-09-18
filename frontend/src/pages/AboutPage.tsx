import React from 'react';
import { Info, Code2, Server, Database, ShieldAlert, Cpu } from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';

import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';

export const AboutPage: React.FC = () => {
  return (
    <div className="relative w-full px-4 sm:px-6 lg:px-8 py-6 space-y-6 fade-in">
      <ScientificMolecularBackground intensity={0.55} />
      {/* Header */}
      <div className="research-card p-6 border-slate-800 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950/90">
        <div className="max-w-3xl space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
              Platform Information &amp; Provenance
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Info className="w-7 h-7 text-cyan-400" />
            <span>About Gene-Cure AI</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            An advanced computational genomics platform for in-silico CRISPR-Cas9 guide RNA design, hybrid deep learning activity prediction, and multi-criteria guide prioritization in oncology.
          </p>
        </div>
      </div>



      {/* Overview & Purpose */}
      <div className="research-card p-6 space-y-4">
        <SectionHeader
          title="Project Purpose &amp; Engineering Philosophy"
          subtitle="Rigorous computational biology standards, data provenance, and scientific integrity"
        />

        <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
          <p>
            <strong>Gene-Cure AI</strong> is engineered to accelerate target discovery and functional genomics screens for breast, lung, and liver malignancies. By combining structural bioinformatics, deep convolutional neural networks, gradient-boosted decision trees, and vector-normalized multi-criteria decision analysis (TOPSIS), the platform delivers transparent, deterministic, and scientifically grounded guide rankings.
          </p>
          <p>
            The software operates strictly under a <strong>no-fabrication policy</strong>: all biological coordinates are traced directly to Ensembl Release 112 and NCBI Gene registries; off-target searches reference the official 2.93 GB GRCh38 primary assembly; and machine learning evaluations are calibrated on empirical Doench 2016 Rule Set 2 knockout activity screens.
          </p>
        </div>
      </div>

      {/* Technology Stack Grid */}
      <div className="research-card p-6 space-y-4">
        <SectionHeader
          title="Core Technology Stack"
          subtitle="Full-stack computational genomics architecture"
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2 text-cyan-400">
              <Code2 size={16} />
              <h3 className="font-bold text-xs">Frontend &amp; 3D WebGL</h3>
            </div>
            <p className="text-[11px] text-slate-400">
              React 18, TypeScript, Vite, TailwindCSS, Three.js, React Three Fiber (@react-three/fiber), @react-three/drei, Recharts.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2 text-blue-400">
              <Server size={16} />
              <h3 className="font-bold text-xs">Backend API Engine</h3>
            </div>
            <p className="text-[11px] text-slate-400">
              FastAPI (Python 3.10), Pydantic v2, SQLAlchemy 2.0 Async, aiosqlite / PostgreSQL, Biopython, NumPy, SciPy.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2 text-indigo-400">
              <Cpu size={16} />
              <h3 className="font-bold text-xs">Machine Learning</h3>
            </div>
            <p className="text-[11px] text-slate-400">
              PyTorch (1D-CNN), XGBoost (105-Feature Vector Regressor), Scikit-Learn (Stacking Meta-Learner).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2 text-emerald-400">
              <Database size={16} />
              <h3 className="font-bold text-xs">Genomics &amp; Indices</h3>
            </div>
            <p className="text-[11px] text-slate-400">
              GRCh38 Primary Assembly Genome, GENCODE v46 GTF, Bowtie2 Genomic Index, CFD Scoring Matrices.
            </p>
          </div>
        </div>
      </div>

      {/* Limitations & Wet-Lab Disclaimer */}
      <div className="research-card p-6 space-y-3 border-amber-500/20 bg-amber-950/10">
        <div className="flex items-center gap-2 text-amber-400">
          <ShieldAlert size={18} />
          <h2 className="text-sm font-bold uppercase tracking-wider">
            Limitations &amp; Wet-Lab Validation Protocol
          </h2>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Computational models represent <em>in-silico</em> approximations of biological Cas9 cleavage kinetics, chromatin accessibility, and microhomology-mediated repair. Guide efficiencies and off-target risks are subject to cell-line-specific epigenetics, chromatin compaction, and transversion frequency. All candidates must undergo experimental validation (e.g., T7 Endonuclease I assays, GUIDE-seq, deep amplicon sequencing) prior to therapeutic or in-vivo investigation.
        </p>
      </div>
    </div>
  );
};
