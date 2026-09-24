import React from 'react';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import { formatSafeText } from '../utils/formatters';

/**
 * Train Header Card: Prominently displays train number, name, type, source, and destination.
 */
export const TrainOverview = ({ trainData }) => {
  if (!trainData || !trainData.train) return null;

  const trainNumber = formatSafeText(trainData.train.train_number);
  const trainName = formatSafeText(trainData.train.train_name);
  const trainType = formatSafeText(trainData.train.train_type);
  const source = formatSafeText(trainData.train.source);
  const destination = formatSafeText(trainData.train.destination);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-xs overflow-hidden">
      <div className="border-b border-slate-200 dark:border-slate-800 px-5 sm:px-6 py-4 bg-gradient-to-r from-slate-900 via-slate-800 to-blue-950 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3 sm:space-x-4 min-w-0 flex-1">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-500 text-white flex items-center justify-center font-mono font-black text-base shadow-sm shrink-0">
            {trainNumber}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center space-x-2.5 flex-wrap">
              <h2 className="text-lg sm:text-xl font-extrabold text-white tracking-tight leading-snug break-words">
                {trainName}
              </h2>
              {trainType !== 'Not available' && (
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-500/20 text-blue-100 border border-blue-400/30 shrink-0">
                  {trainType}
                </span>
              )}
            </div>
            <div className="text-xs text-slate-300 mt-1 flex items-center space-x-2 flex-wrap">
              <span className="font-mono font-medium">Train #{trainNumber}</span>
              <span>•</span>
              <span className="font-medium text-slate-200">Active Corridor</span>
            </div>
          </div>
        </div>

        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-200 text-xs font-medium border border-emerald-400/30 shrink-0">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-300 shrink-0" />
          <span>Live Telemetry</span>
        </div>
      </div>

      <div className="px-5 sm:px-6 py-4 bg-white dark:bg-slate-900">
        <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400 dark:text-slate-500 mb-2">
          Route Corridor
        </div>
        <div className="flex items-center justify-between flex-wrap gap-2 text-sm sm:text-base font-bold text-slate-800 dark:text-slate-200 bg-slate-50 dark:bg-slate-800/60 px-4 py-3 rounded-xl border border-slate-200/80 dark:border-slate-700/80">
          <div className="flex items-center space-x-2 min-w-0 flex-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shrink-0" />
            <span className="truncate" title={source}>{source}</span>
          </div>

          <div className="flex items-center space-x-2 text-blue-500 px-2 shrink-0">
            <span className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400 hidden md:inline">Route</span>
            <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5" />
          </div>

          <div className="flex items-center space-x-2 min-w-0 flex-1 justify-end text-right">
            <span className="truncate" title={destination}>{destination}</span>
            <span className="w-2.5 h-2.5 rounded-full bg-sky-500 shrink-0" />
          </div>
        </div>
      </div>

      <div className="px-5 sm:px-6 pb-4 pt-1 grid grid-cols-2 sm:grid-cols-4 gap-3 border-t border-slate-100 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-850">
        <div className="p-2.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200/80 dark:border-slate-700">
          <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase">Train No.</div>
          <div className="text-sm font-bold font-mono text-slate-900 dark:text-white mt-0.5">{trainNumber}</div>
        </div>
        <div className="p-2.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200/80 dark:border-slate-700">
          <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase">Service</div>
          <div className="text-sm font-bold text-slate-900 dark:text-white mt-0.5">{trainType}</div>
        </div>
        <div className="p-2.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200/80 dark:border-slate-700">
          <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase">From</div>
          <div className="text-sm font-bold text-slate-900 dark:text-white mt-0.5 truncate" title={source}>{source}</div>
        </div>
        <div className="p-2.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200/80 dark:border-slate-700">
          <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase">To</div>
          <div className="text-sm font-bold text-slate-900 dark:text-white mt-0.5 truncate" title={destination}>{destination}</div>
        </div>
      </div>
    </div>
  );
};

export default TrainOverview;
