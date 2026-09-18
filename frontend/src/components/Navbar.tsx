import React from 'react';
import { Dna, Activity, Cpu } from 'lucide-react';
import { HealthResponse } from '../types';

interface NavbarProps {
  health: HealthResponse | null;
}

export const Navbar: React.FC<NavbarProps> = ({ health }) => {
  const isDemo = health?.execution_mode === 'DEMO_MODE';

  return (
    <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
      <div className="w-full px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-sky-500/20 p-2 rounded-xl border border-sky-500/30 text-sky-400">
            <Dna className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <span className="font-bold text-lg text-white tracking-tight">Gene-Cure AI</span>
            <span className="text-xs ml-2 text-sky-400 font-mono">v{health?.version || '1.0'}</span>
          </div>
        </div>

        <nav className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400">System Mode:</span>
            {isDemo ? (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/30">
                <Cpu className="w-3 h-3 mr-1" /> DEMO MODE
              </span>
            ) : (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                <Activity className="w-3 h-3 mr-1" /> REAL MODE
              </span>
            )}
          </div>
        </nav>
      </div>
    </nav>
  );
};
