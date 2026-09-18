import React from 'react';
import { StatusBadge, StatusType } from './StatusBadge';

interface SystemStatusRowProps {
  name: string;
  description: string;
  status: StatusType | string;
  pathOrDetail?: string;
}

export const SystemStatusRow: React.FC<SystemStatusRowProps> = ({
  name,
  description,
  status,
  pathOrDetail,
}) => {
  return (
    <div className="flex items-center justify-between py-2.5 px-3 border-b border-slate-800/60 last:border-b-0 hover:bg-slate-800/20 rounded-md transition-colors">
      <div className="flex flex-col min-w-0 pr-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-200">{name}</span>
        </div>
        <span className="text-[11px] text-slate-400 truncate">{description}</span>
        {pathOrDetail && (
          <span className="text-[10px] font-mono text-slate-500 truncate mt-0.5">
            {pathOrDetail}
          </span>
        )}
      </div>
      <div className="flex-shrink-0">
        <StatusBadge status={status} />
      </div>
    </div>
  );
};
