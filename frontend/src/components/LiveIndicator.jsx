import React from 'react';
import { RefreshCw, Radio, AlertTriangle } from 'lucide-react';

/**
 * Small global live-data indicator near dashboard title
 * Complies with requirement: Real-time update status, time ago, manual refresh trigger.
 */
export const LiveIndicator = ({
  lastUpdated = null,
  timeAgo = 'Just now',
  isRefreshing = false,
  refreshError = null,
  onRefresh = () => {},
  telemetrySource = 'live_railradar',
}) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 py-2 px-3 rounded-xl bg-slate-100/70 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 text-xs">
      {/* Left: Live status */}
      <div className="flex items-center space-x-2.5">
        <span className="relative flex h-2.5 w-2.5">
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
              isRefreshing ? 'bg-amber-400' : 'bg-emerald-400'
            }`}
          />
          <span
            className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
              isRefreshing ? 'bg-amber-500' : 'bg-emerald-500'
            }`}
          />
        </span>

        <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5 uppercase tracking-wide text-[11px]">
          LIVE
        </span>

        <span className="text-slate-300 dark:text-slate-600">•</span>

        <span className="text-slate-600 dark:text-slate-300 flex items-center gap-1">
          <Radio className="w-3 h-3 text-emerald-500 shrink-0" />
          <span>Updating automatically</span>
        </span>

        <span className="hidden sm:inline-block text-slate-300 dark:text-slate-600">•</span>

        <span className="hidden sm:inline-block text-slate-500 dark:text-slate-400 text-[11px]">
          {telemetrySource === 'live_railradar' ? 'Connected to RailRadar API' : 'Real-time Indian Railways schedule'}
        </span>
      </div>

      {/* Right: Last updated & Refresh button */}
      <div className="flex items-center space-x-3 ml-auto">
        {refreshError && (
          <div className="flex items-center space-x-1.5 text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/60 px-2 py-0.5 rounded text-[11px] border border-amber-200 dark:border-amber-800">
            <AlertTriangle className="w-3 h-3 shrink-0" />
            <span className="truncate max-w-[200px]">{refreshError}</span>
          </div>
        )}

        <div className="text-slate-500 dark:text-slate-400 text-[11px]">
          Last updated:{' '}
          <span className="font-semibold text-slate-800 dark:text-slate-200 font-mono">
            {timeAgo}
          </span>
        </div>

        <button
          type="button"
          onClick={onRefresh}
          disabled={isRefreshing}
          title="Refresh live data now"
          className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-white dark:bg-slate-700 hover:bg-slate-50 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-600 shadow-2xs font-medium transition cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw
            className={`w-3 h-3 ${isRefreshing ? 'animate-spin text-blue-600 dark:text-blue-400' : ''}`}
          />
          <span className="text-[11px]">Refresh</span>
        </button>
      </div>
    </div>
  );
};

export default LiveIndicator;
