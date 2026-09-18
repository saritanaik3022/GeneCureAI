import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800 bg-slate-950 py-8 text-center text-xs text-slate-500">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <p className="mb-2">Gene-Cure AI: A Deep Learning-Driven Platform for Automated CRISPR Guide RNA Design.</p>
        <p className="text-slate-600">Targeting Breast, Lung, and Liver Cancer Therapeutics &copy; 2026</p>
      </div>
    </footer>
  );
};
