import React, { useEffect, useState } from 'react';
import { Dna, Target, Activity, ShieldCheck, Award, Layers } from 'lucide-react';

import { CancerGene } from '../types';
import { fetchCancerGenes } from '../services/api';

export const HomePage: React.FC = () => {
  const [genes, setGenes] = useState<CancerGene[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchCancerGenes()
      .then((data) => {
        setGenes(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load genes', err);
        setLoading(false);
      });
  }, []);

  const stages = [
    { num: '01', title: 'Cancer Gene Selection', desc: 'Curated oncology target registry with NCBI & Ensembl provenance.', icon: Target },
    { num: '02', title: 'Guide RNA Identification', desc: 'SpCas9 dual-strand scanning for 20-nt protospacers + 5\'-NGG PAM.', icon: Dna },
    { num: '03', title: 'On-Target Efficiency', desc: 'Hybrid PyTorch 1D-CNN + XGBoost 105 engineered feature ensemble.', icon: Activity },
    { num: '04', title: 'Off-Target Safety', desc: 'GRCh38 seed-and-extend alignment with Cutting Frequency Determination (CFD).', icon: ShieldCheck },
    { num: '05', title: 'TOPSIS Ranking', desc: 'Multi-criteria decision analysis (35% On-target, 30% Safety, 20% Cancer, 15% GC).', icon: Award },
  ];

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 py-10">
      {/* Hero Section */}
      <div className="text-center max-w-3xl mx-auto">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-semibold mb-4">
          <Layers className="w-3.5 h-3.5" />
          <span>In-Silico CRISPR Design Architecture</span>
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">
          Automated CRISPR Guide RNA Design for Cancer Therapeutics
        </h1>
        <p className="mt-4 text-lg text-slate-400">
          Targeting Breast, Lung, and Liver Cancers with Deep Learning Sequence Representations,
          105-Feature XGBoost Regression, and TOPSIS Multi-Criteria Decision Ranking.
        </p>
      </div>



      {/* 5-Stage Pipeline Overview */}
      <div className="mt-12">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center space-x-2">
          <Layers className="w-5 h-5 text-sky-400" />
          <span>Five-Stage Computational Pipeline</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {stages.map((stage) => {
            const Icon = stage.icon;
            return (
              <div key={stage.num} className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 hover:border-sky-500/40 transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-mono font-bold text-sky-400">{stage.num}</span>
                  <Icon className="w-5 h-5 text-slate-400" />
                </div>
                <h3 className="font-semibold text-white text-sm mb-1">{stage.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{stage.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Target Cancer Genes Section */}
      <div className="mt-16">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center space-x-2">
          <Target className="w-5 h-5 text-sky-400" />
          <span>Curated Target Cancer Genes</span>
        </h2>
        {loading ? (
          <div className="text-center py-10 text-slate-400 text-sm">Loading curated cancer genes...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {genes.map((gene) => (
              <div key={gene.symbol} className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-5 hover:bg-slate-800/70 transition-all">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-lg text-white">{gene.symbol}</span>
                  <span className="text-xs font-mono text-slate-400">Chr {gene.chromosome}:{gene.genomic_start.toLocaleString()}</span>
                </div>
                <p className="text-xs text-slate-300 font-medium mb-3">{gene.name}</p>
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {gene.cancer_types.map((ct) => (
                    <span key={ct} className="px-2 py-0.5 rounded text-[11px] font-medium bg-sky-950 text-sky-300 border border-sky-800/50">
                      {ct}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-slate-400 line-clamp-2">{gene.cancer_relevance_summary}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
