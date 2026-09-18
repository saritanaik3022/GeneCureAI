import React from 'react';
import { HelpCircle, Beaker, Dna } from 'lucide-react';
import type { HealthResponse } from '../../types';

interface TopNavProps {
  health: HealthResponse | null;
  loading: boolean;
  backendError: string | null;
}

export const TopNav: React.FC<TopNavProps> = ({ health, loading, backendError }) => {
  const isOnline = !loading && !!health && !backendError && (health.status === 'ok' || health.status === 'healthy' || !!health.status);
  const mode = health?.execution_mode || 'REAL_MODE';

  let statusClass: string;

  if (loading) {
    statusClass = 'connecting';
  } else if (!isOnline) {
    statusClass = 'offline';
  } else {
    statusClass = 'online';
  }

  return (
    <header
      className="fixed top-0 left-0 right-0 flex items-center justify-between px-4"
      style={{
        height: 'var(--topnav-height)',
        background: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border-subtle)',
        zIndex: 50,
        backdropFilter: 'blur(12px)',
      }}
      role="banner"
    >
      {/* Left: Brand */}
      <div className="flex items-center gap-3">
        <div
          className="flex items-center justify-center w-8 h-8 rounded-lg"
          style={{ background: 'rgba(34,211,238,0.12)', border: '1px solid rgba(34,211,238,0.2)' }}
        >
          <Dna size={16} style={{ color: 'var(--accent-cyan)' }} />
        </div>
        <div>
          <div className="flex items-baseline gap-2">
            <span className="text-sm font-bold tracking-wide" style={{ color: 'var(--text-primary)' }}>
              GENE-CURE AI
            </span>
            <span
              className="hidden sm:block text-[10px] font-mono"
              style={{ color: 'var(--text-muted)' }}
            >
              CRISPR Guide RNA Design &amp; Computational Analysis
            </span>
          </div>
        </div>
      </div>

      {/* Right: Status + Mode + Actions */}
      <div className="flex items-center gap-4">
        {/* Backend Status — live from health endpoint */}
        <div className="flex items-center gap-2">
          <span className={`status-dot ${statusClass}`} aria-label={isOnline ? 'Backend Online' : 'Backend Offline'} />
          {loading ? (
            <span className="text-xs font-mono font-medium text-slate-400">
              Connecting...
            </span>
          ) : isOnline ? (
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-medium" style={{ color: '#34d399' }}>
                Backend Online
              </span>
              <span
                className="text-[10px] font-mono font-bold px-2 py-0.5 rounded border"
                style={{
                  color: mode === 'REAL_MODE' ? '#22d3ee' : '#f59e0b',
                  borderColor: mode === 'REAL_MODE' ? 'rgba(34,211,238,0.4)' : 'rgba(245,158,11,0.4)',
                  background: mode === 'REAL_MODE' ? 'rgba(34,211,238,0.1)' : 'rgba(245,158,11,0.1)',
                }}
              >
                {mode}
              </span>
            </div>
          ) : (
            <span className="text-xs font-mono font-medium" style={{ color: '#f87171' }}>
              Backend Offline
            </span>
          )}
        </div>

        {/* Research Workspace indicator */}
        <div className="hidden md:flex items-center gap-1.5">
          <Beaker size={13} style={{ color: 'var(--text-muted)' }} />
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
            Research Workspace
          </span>
        </div>

        {/* Help */}
        <button
          className="flex items-center gap-1 text-xs rounded-md px-2 py-1 transition-colors"
          style={{ color: 'var(--text-muted)' }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-primary)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
          aria-label="Help"
        >
          <HelpCircle size={13} />
          <span className="hidden sm:inline">Help</span>
        </button>
      </div>
    </header>
  );
};
