import React from 'react';

export type StatusType = 'READY' | 'NOT_READY' | 'NOT_AVAILABLE' | 'ERROR' | 'CHECKING' | 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'SUCCESS';

interface StatusBadgeProps {
  status: StatusType | string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const norm = status.toUpperCase();

  let bg = 'rgba(148, 163, 184, 0.1)';
  let text = '#94a3b8';
  let border = 'rgba(148, 163, 184, 0.2)';

  if (norm === 'READY' || norm === 'COMPLETED' || norm === 'SUCCESS' || norm === 'HEALTHY' || norm === 'ONLINE') {
    bg = 'rgba(16, 185, 129, 0.1)';
    text = '#10b981';
    border = 'rgba(16, 185, 129, 0.25)';
  } else if (norm === 'RUNNING' || norm === 'CHECKING' || norm === 'PENDING') {
    bg = 'rgba(14, 165, 233, 0.1)';
    text = '#0ea5e9';
    border = 'rgba(14, 165, 233, 0.25)';
  } else if (norm === 'NOT_READY' || norm === 'MODEL_NOT_READY' || norm === 'WARNING') {
    bg = 'rgba(245, 158, 11, 0.1)';
    text = '#f59e0b';
    border = 'rgba(245, 158, 11, 0.25)';
  } else if (norm === 'FAILED' || norm === 'ERROR' || norm === 'NOT_AVAILABLE' || norm === 'OFFLINE') {
    bg = 'rgba(239, 68, 68, 0.1)';
    text = '#ef4444';
    border = 'rgba(239, 68, 68, 0.25)';
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase border ${className}`}
      style={{ backgroundColor: bg, color: text, borderColor: border }}
    >
      {norm.replace(/_/g, ' ')}
    </span>
  );
};
