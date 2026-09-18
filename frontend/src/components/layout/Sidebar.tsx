import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Boxes,
  Activity,
  Target,
  ShieldAlert,
  BarChart3,
  GitCompareArrows,
  Cpu,
  History,
  FileText,
  BookOpen,
  Info,
  Dna,
  Award,
} from 'lucide-react';

interface NavItem {
  path: string;
  label: string;
  icon: React.ElementType;
  group?: string;
}

const NAV_ITEMS: NavItem[] = [
  { path: '/dashboard',          label: 'Dashboard',          icon: LayoutDashboard, group: 'main' },
  { path: '/design-studio',      label: 'Design Studio',      icon: Boxes,           group: 'main' },
  { path: '/analysis-pipeline',  label: 'Analysis Pipeline',  icon: Activity,        group: 'analysis' },
  { path: '/ranked-guides',      label: 'Ranked Guide RNAs',  icon: Award,           group: 'analysis' },
  { path: '/grna-candidates',    label: 'gRNA Candidates',    icon: Target,          group: 'analysis' },
  { path: '/off-target',         label: 'Off-Target Analysis',icon: ShieldAlert,     group: 'analysis' },
  { path: '/topsis-ranking',     label: 'TOPSIS Ranking',     icon: BarChart3,       group: 'analysis' },
  { path: '/compare-guides',     label: 'Compare Guides',     icon: GitCompareArrows,group: 'analysis' },
  { path: '/model-performance',  label: 'Model Performance',  icon: Cpu,             group: 'ml' },
  { path: '/analysis-history',   label: 'Analysis History',   icon: History,         group: 'data' },
  { path: '/reports',            label: 'Reports',            icon: FileText,        group: 'data' },
  { path: '/methodology',        label: 'Methodology',        icon: BookOpen,        group: 'info' },
  { path: '/about',              label: 'About',              icon: Info,            group: 'info' },
];

const GROUP_LABELS: Record<string, string> = {
  main: 'Overview',
  analysis: 'Pipeline Stages',
  ml: 'Machine Learning',
  data: 'Data & Reports',
  info: 'Documentation',
};

export const Sidebar: React.FC = () => {
  const location = useLocation();

  // Group items
  const groups = NAV_ITEMS.reduce<Record<string, NavItem[]>>((acc, item) => {
    const g = item.group ?? 'main';
    if (!acc[g]) acc[g] = [];
    acc[g].push(item);
    return acc;
  }, {});

  const groupOrder = ['main', 'analysis', 'ml', 'data', 'info'];

  return (
    <aside
      className="fixed top-0 left-0 h-full flex flex-col overflow-y-auto"
      style={{
        width: 'var(--sidebar-width)',
        marginTop: 'var(--topnav-height)',
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border-subtle)',
        zIndex: 40,
      }}
      aria-label="Research workspace navigation"
    >
      {/* Sidebar Header */}
      <div className="px-4 py-4 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
        <div className="flex items-center gap-2 mb-1">
          <div
            className="w-6 h-6 rounded flex items-center justify-center"
            style={{ background: 'rgba(34,211,238,0.12)' }}
          >
            <Dna size={13} style={{ color: 'var(--accent-cyan)' }} />
          </div>
          <span
            className="text-xs font-bold tracking-widest uppercase"
            style={{ color: 'var(--text-muted)', letterSpacing: '0.1em' }}
          >
            Research Workspace
          </span>
        </div>
        <p className="text-[10px] leading-snug" style={{ color: 'var(--text-muted)', paddingLeft: '1.75rem' }}>
          In-silico CRISPR guide design &amp; computational analysis
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-3 space-y-4" aria-label="Main navigation">
        {groupOrder.map((groupKey) => {
          const items = groups[groupKey];
          if (!items) return null;
          return (
            <div key={groupKey}>
              <div
                className="px-2 mb-1 text-[10px] font-semibold tracking-widest uppercase"
                style={{ color: 'var(--text-muted)' }}
              >
                {GROUP_LABELS[groupKey]}
              </div>
              <div className="space-y-0.5">
                {items.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path ||
                    (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      className={`nav-item${isActive ? ' active' : ''}`}
                      aria-current={isActive ? 'page' : undefined}
                    >
                      <Icon
                        size={14}
                        className="nav-icon flex-shrink-0"
                        style={{ color: isActive ? 'var(--accent-cyan)' : 'var(--text-muted)' }}
                      />
                      <span className="truncate">{item.label}</span>
                      {item.path === '/design-studio' && (
                        <span
                          className="ml-auto text-[9px] px-1 rounded font-bold"
                          style={{
                            background: 'rgba(34,211,238,0.12)',
                            color: 'var(--accent-cyan)',
                          }}
                        >
                          3D
                        </span>
                      )}
                    </NavLink>
                  );
                })}
              </div>
            </div>
          );
        })}
      </nav>

      {/* Sidebar Footer */}
      <div className="px-3 py-3 border-t" style={{ borderColor: 'var(--border-subtle)' }}>
        <p className="text-[10px] leading-snug" style={{ color: 'var(--text-muted)' }}>
          Gene-Cure AI v1.0.0
        </p>
        <p className="text-[9px] mt-0.5" style={{ color: 'var(--text-muted)', opacity: 0.6 }}>
          In-silico predictions only. Not for clinical use.
        </p>
      </div>
    </aside>
  );
};
