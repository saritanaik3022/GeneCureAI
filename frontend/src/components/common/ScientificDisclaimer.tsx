import React from 'react';
import { ShieldAlert } from 'lucide-react';

interface ScientificDisclaimerProps {
  compact?: boolean;
}

export const ScientificDisclaimer: React.FC<ScientificDisclaimerProps> = ({ compact = false }) => {
  if (compact) {
    return (
      <div 
        className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs"
        style={{
          background: 'rgba(245, 158, 11, 0.05)',
          border: '1px solid rgba(245, 158, 11, 0.2)',
          color: '#fbbf24'
        }}
      >
        <ShieldAlert size={14} className="flex-shrink-0" />
        <span>
          <strong>Scientific Disclaimer:</strong> In-silico computational predictions only. Not for clinical treatment or experimental diagnostic use without wet-lab validation.
        </span>
      </div>
    );
  }

  return (
    <div
      className="research-card p-4 rounded-xl flex items-start gap-3 my-4"
      style={{
        background: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(245, 158, 11, 0.25)'
      }}
    >
      <div
        className="p-2 rounded-lg flex items-center justify-center flex-shrink-0"
        style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b' }}
      >
        <ShieldAlert size={18} />
      </div>
      <div className="text-xs space-y-1">
        <h4 className="font-semibold text-amber-400 uppercase tracking-wider text-[11px]">
          Mandatory Research &amp; Clinical Disclaimer
        </h4>
        <p className="text-slate-300 leading-relaxed">
          This platform provides <em>in-silico</em> computational predictions and is not a substitute for experimental validation in molecular biology or clinical laboratories. All generated guide RNAs, efficiency predictions, and off-target safety evaluations must undergo wet-lab functional validation before any biological or therapeutic application.
        </p>
        <p className="text-[11px] text-slate-400">
          The software does not physically edit DNA. All representations and cleavage sites are computational simulations based on mathematical and machine learning models.
        </p>
      </div>
    </div>
  );
};
