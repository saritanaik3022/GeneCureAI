import React from 'react';
import { ExecutionMode } from '../../types';

interface ModeBadgeProps {
  mode: ExecutionMode | string;
  className?: string;
}

export const ModeBadge: React.FC<ModeBadgeProps> = ({ mode, className = '' }) => {
  const isDemo = mode === 'DEMO_MODE' || mode === 'DEMO';

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-mono font-bold tracking-wider uppercase border ${
        isDemo ? 'badge-demo' : 'badge-real'
      } ${className}`}
    >
      {isDemo ? 'DEMO MODE' : 'REAL MODE'}
    </span>
  );
};
