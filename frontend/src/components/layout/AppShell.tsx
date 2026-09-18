import React from 'react';
import { TopNav } from './TopNav';
import { Sidebar } from './Sidebar';
import { AppRouter } from '../../routes/AppRouter';
import { useHealth } from '../../hooks/useHealth';

export const AppShell: React.FC = () => {
  const { health, loading, error } = useHealth();

  return (
    <div className="flex flex-col min-h-screen h-full w-full overflow-x-hidden" style={{ background: 'var(--bg-base)' }}>
      {/* Fixed Top Navigation */}
      <TopNav health={health} loading={loading} backendError={error} />

      {/* Body: Sidebar + Content */}
      <div
        className="flex flex-1 min-h-[calc(100vh-var(--topnav-height))] w-full overflow-hidden"
        style={{ paddingTop: 'var(--topnav-height)' }}
      >
        {/* Fixed Sidebar */}
        <Sidebar />

        {/* Main routed content filling remaining viewport */}
        <main
          className="flex-1 min-w-0 w-full overflow-y-auto overflow-x-hidden flex flex-col"
          style={{ marginLeft: 'var(--sidebar-width)' }}
        >
          <div className="flex-1 w-full min-h-full">
            <AppRouter />
          </div>
        </main>
      </div>
    </div>
  );
};
