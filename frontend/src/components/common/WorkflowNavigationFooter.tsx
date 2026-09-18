import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight } from 'lucide-react';

interface WorkflowNavigationFooterProps {
  prevPath?: string;
  prevLabel?: string;
  nextPath?: string;
  nextLabel?: string;
  nextDisabled?: boolean;
  onNext?: () => void;
}

export const WorkflowNavigationFooter: React.FC<WorkflowNavigationFooterProps> = ({
  prevPath,
  prevLabel,
  nextPath,
  nextLabel,
  nextDisabled = false,
  onNext,
}) => {
  const navigate = useNavigate();

  return (
    <div className="mt-8 pt-5 border-t border-slate-800/80 flex items-center justify-between gap-4">
      {prevPath ? (
        <button
          onClick={() => navigate(prevPath)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white bg-slate-900/80 hover:bg-slate-800 border border-slate-700/60 shadow-sm transition-all cursor-pointer group"
        >
          <ArrowLeft size={14} className="text-cyan-400 group-hover:-translate-x-0.5 transition-transform" />
          <span>{prevLabel || 'Previous Step'}</span>
        </button>
      ) : (
        <div />
      )}

      {nextPath ? (
        <button
          onClick={() => {
            if (onNext) onNext();
            navigate(nextPath);
          }}
          disabled={nextDisabled}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-cyan-500 hover:bg-cyan-400 disabled:opacity-40 disabled:cursor-not-allowed text-slate-950 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer group"
        >
          <span>{nextLabel || 'Next Step'}</span>
          <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
        </button>
      ) : (
        <div />
      )}
    </div>
  );
};
