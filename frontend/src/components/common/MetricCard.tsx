import React from 'react';
import type { ReactNode } from 'react';
import { clsx } from 'clsx';

interface MetricCardProps {
  label: string;
  value: ReactNode;
  subtitle?: string;
  icon?: ReactNode;
  accent?: 'cyan' | 'blue' | 'teal' | 'green' | 'amber' | 'red';
  size?: 'sm' | 'md';
  className?: string;
}

const ACCENT_STYLES: Record<string, { iconBg: string; valueCls: string; border: string }> = {
  cyan:  { iconBg: 'rgba(34,211,238,0.12)',  valueCls: '#22d3ee', border: 'rgba(34,211,238,0.15)' },
  blue:  { iconBg: 'rgba(59,130,246,0.12)',  valueCls: '#60a5fa', border: 'rgba(59,130,246,0.15)' },
  teal:  { iconBg: 'rgba(20,184,166,0.12)',  valueCls: '#2dd4bf', border: 'rgba(20,184,166,0.15)' },
  green: { iconBg: 'rgba(16,185,129,0.12)',  valueCls: '#34d399', border: 'rgba(16,185,129,0.15)' },
  amber: { iconBg: 'rgba(245,158,11,0.12)',  valueCls: '#fbbf24', border: 'rgba(245,158,11,0.15)' },
  red:   { iconBg: 'rgba(239,68,68,0.12)',   valueCls: '#f87171', border: 'rgba(239,68,68,0.15)' },
};

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtitle,
  icon,
  accent = 'cyan',
  size = 'md',
  className,
}) => {
  const styles = ACCENT_STYLES[accent];

  return (
    <div
      className={clsx('research-card p-4 flex flex-col gap-2', className)}
      style={{ borderColor: styles.border }}
    >
      <div className="flex items-center justify-between">
        <span
          className="text-xs font-semibold tracking-widest uppercase"
          style={{ color: 'var(--text-muted)', letterSpacing: '0.08em' }}
        >
          {label}
        </span>
        {icon && (
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ background: styles.iconBg }}
          >
            {icon}
          </div>
        )}
      </div>

      <div
        className={clsx('font-extrabold leading-none tracking-tight', size === 'md' ? 'text-3xl' : 'text-xl')}
        style={{ color: styles.valueCls }}
      >
        {value}
      </div>

      {subtitle && (
        <p className="text-[11px] leading-snug" style={{ color: 'var(--text-muted)' }}>
          {subtitle}
        </p>
      )}
    </div>
  );
};
