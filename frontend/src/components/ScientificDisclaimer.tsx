import React from 'react';
import { AlertTriangle } from 'lucide-react';

export const ScientificDisclaimer: React.FC = () => {
  return (
    <div className="bg-amber-950/40 border border-amber-500/30 rounded-xl p-4 my-6 text-amber-200 text-sm flex items-start space-x-3">
      <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
      <div>
        <h4 className="font-semibold text-amber-300">Scientific Validation Disclaimer</h4>
        <p className="text-xs text-amber-200/80 mt-1">
          This platform provides <em>in-silico</em> computational predictions and is not a substitute for experimental validation
          in molecular biology or clinical laboratories. All generated guide RNAs, efficiency predictions, and off-target safety
          evaluations must undergo wet-lab functional validation before any biological or therapeutic application.
        </p>
      </div>
    </div>
  );
};
