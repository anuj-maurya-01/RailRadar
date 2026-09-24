import React from 'react';
import { CheckCircle2, Clock, AlertTriangle, XCircle, Radio, Flag, MinusCircle } from 'lucide-react';

/**
 * Reusable Train Status Badge Component
 * Complies with requirement: Never rely on color alone; includes icon, text, and accessible pill styling.
 */
export const StatusBadge = ({
  status = 'on_time',
  delayMinutes = 0,
  size = 'md', // 'sm' | 'md' | 'lg'
  className = '',
}) => {
  const normStatus = String(status || '').toLowerCase().trim();
  const numDelay = Number(delayMinutes) || 0;

  let badgeType = 'on_time';
  if (normStatus === 'cancelled') {
    badgeType = 'cancelled';
  } else if (normStatus === 'delayed' || numDelay > 5) {
    badgeType = 'delayed';
  } else if (normStatus === 'arrived' || normStatus === 'completed') {
    badgeType = 'arrived';
  } else if (normStatus === 'not_started' || normStatus === 'scheduled') {
    badgeType = 'not_started';
  } else if (normStatus === 'in_transit' || normStatus === 'departed' || normStatus === 'running') {
    badgeType = numDelay > 5 ? 'delayed' : 'running';
  }

  // Size styling classes
  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-semibold',
  }[size] || 'text-xs px-2.5 py-1 gap-1.5';

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  }[size] || 'w-3.5 h-3.5';

  switch (badgeType) {
    case 'on_time':
      return (
        <span
          className={`inline-flex items-center rounded-full font-semibold bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/25 shadow-xs ${sizeClasses} ${className}`}
        >
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500" />
          </span>
          <span>ON TIME</span>
        </span>
      );

    case 'delayed':
      return (
        <span
          className={`inline-flex items-center rounded-full font-semibold bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/25 shadow-xs ${sizeClasses} ${className}`}
        >
          <Clock className={`${iconSizes} shrink-0`} />
          <span>{numDelay > 0 ? `${numDelay} MIN DELAY` : 'DELAYED'}</span>
        </span>
      );

    case 'cancelled':
      return (
        <span
          className={`inline-flex items-center rounded-full font-semibold bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/25 shadow-xs ${sizeClasses} ${className}`}
        >
          <XCircle className={`${iconSizes} shrink-0`} />
          <span>CANCELLED</span>
        </span>
      );

    case 'arrived':
      return (
        <span
          className={`inline-flex items-center rounded-full font-semibold bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 border border-indigo-500/25 shadow-xs ${sizeClasses} ${className}`}
        >
          <Flag className={`${iconSizes} shrink-0`} />
          <span>ARRIVED</span>
        </span>
      );

    case 'not_started':
      return (
        <span
          className={`inline-flex items-center rounded-full font-medium bg-slate-500/10 text-slate-600 dark:text-slate-400 border border-slate-500/20 shadow-xs ${sizeClasses} ${className}`}
        >
          <MinusCircle className={`${iconSizes} shrink-0`} />
          <span>NOT STARTED</span>
        </span>
      );

    case 'running':
    default:
      return (
        <span
          className={`inline-flex items-center rounded-full font-semibold bg-sky-500/10 text-sky-700 dark:text-sky-400 border border-sky-500/25 shadow-xs ${sizeClasses} ${className}`}
        >
          <Radio className={`${iconSizes} shrink-0 text-sky-500 animate-pulse`} />
          <span>RUNNING</span>
        </span>
      );
  }
};

export default StatusBadge;
