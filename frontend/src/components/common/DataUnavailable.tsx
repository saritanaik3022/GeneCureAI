import React from 'react';
import { AlertTriangle, Info } from 'lucide-react';

interface DataUnavailableProps {
  reason: 'MODEL_NOT_READY' | 'NOT_YET_COMPUTED' | 'DATA_NOT_AVAILABLE' | 'DEMO_MODE' | 'GENOME_NOT_AVAILABLE';
  detail?: string;
  compact?: boolean;
}

const REASON_CONFIG = {
  MODEL_NOT_READY: {
    label: 'MODEL NOT READY',
    detail: 'ML models have not been trained yet. Run the training pipeline to generate evaluation metrics.',
    color: '#f59e0b',
    bg: 'rgba(245,158,11,0.06)',
    border: 'rgba(245,158,11,0.2)',
    Icon: AlertTriangle,
  },
  NOT_YET_COMPUTED: {
    label: 'NOT YET COMPUTED',
    detail: 'This value will be available after the analysis pipeline has completed.',
    color: '#94a3b8',
    bg: 'rgba(148,163,184,0.04)',
    border: 'rgba(148,163,184,0.12)',
    Icon: Info,
  },
  DATA_NOT_AVAILABLE: {
    label: 'DATA NOT AVAILABLE',
    detail: 'Required data resources are not yet loaded.',
    color: '#ef4444',
    bg: 'rgba(239,68,68,0.06)',
    border: 'rgba(239,68,68,0.2)',
    Icon: AlertTriangle,
  },
  DEMO_MODE: {
    label: 'DEMO MODE',
    detail: 'Showing deterministic demonstration fixtures. Run in REAL_MODE with real data for actual results.',
    color: '#f59e0b',
    bg: 'rgba(245,158,11,0.06)',
    border: 'rgba(245,158,11,0.2)',
    Icon: Info,
  },
  GENOME_NOT_AVAILABLE: {
    label: 'GENOME NOT AVAILABLE',
    detail: 'GRCh38 reference genome or Bowtie2 index is not accessible. Off-target analysis requires genomic data.',
    color: '#ef4444',
    bg: 'rgba(239,68,68,0.06)',
    border: 'rgba(239,68,68,0.2)',
    Icon: AlertTriangle,
  },
};

export const DataUnavailable: React.FC<DataUnavailableProps> = ({ reason, detail, compact = false }) => {
  const cfg = REASON_CONFIG[reason];
  const { Icon } = cfg;

  if (compact) {
    return (
      <span
        className="inline-flex items-center gap-1 text-xs font-mono font-semibold px-2 py-0.5 rounded"
        style={{ color: cfg.color, background: cfg.bg, border: `1px solid ${cfg.border}` }}
      >
        <Icon size={10} />
        {cfg.label}
      </span>
    );
  }

  return (
    <div
      className="rounded-xl p-4 flex items-start gap-3"
      style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}
      role="status"
      aria-label={cfg.label}
    >
      <Icon size={16} style={{ color: cfg.color, flexShrink: 0, marginTop: 1 }} />
      <div>
        <div className="text-xs font-bold font-mono mb-1" style={{ color: cfg.color }}>
          {cfg.label}
        </div>
        <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          {detail ?? cfg.detail}
        </p>
      </div>
    </div>
  );
};
