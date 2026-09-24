import React from 'react';
import { ArrowRight, MapPin, Gauge, Clock, Sparkles, Navigation, ChevronDown, CheckCircle2, AlertCircle } from 'lucide-react';
import StatusBadge from './StatusBadge';
import { formatSafeText, formatDelayDisplay, formatSpeed, formatTimeDisplay } from '../utils/formatters';

/**
 * Selected Train Panel (40% Column in the 60/40 layout)
 * Displays compact, high-density telemetry and ML prediction for the active train.
 */
export const SelectedTrainPanel = ({
  trainData = null,
  selectedSummary = null,
  loading = false,
  onInspectDetails = () => {},
  onCenterMap = () => {},
}) => {
  // If loading a specific train
  if (loading) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 p-6 shadow-xs h-full flex flex-col justify-between animate-pulse">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="w-20 h-7 bg-slate-200 dark:bg-slate-800 rounded-lg" />
            <div className="w-24 h-6 bg-slate-200 dark:bg-slate-800 rounded-full" />
          </div>
          <div className="w-48 h-6 bg-slate-200 dark:bg-slate-800 rounded" />
          <div className="w-64 h-4 bg-slate-200 dark:bg-slate-800 rounded" />
          <div className="grid grid-cols-2 gap-3 pt-4">
            <div className="h-16 bg-slate-100 dark:bg-slate-800/60 rounded-xl" />
            <div className="h-16 bg-slate-100 dark:bg-slate-800/60 rounded-xl" />
          </div>
        </div>
        <div className="h-10 bg-slate-200 dark:bg-slate-800 rounded-xl mt-6" />
      </div>
    );
  }

  // Active train resolved from either full trainData or summary selected from table
  const trainObj = trainData?.train || selectedSummary;
  const liveStatus = trainData?.live_status || selectedSummary;
  const prediction = trainData?.prediction;

  if (!trainObj) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 p-6 shadow-xs h-full flex flex-col items-center justify-center text-center">
        <div className="w-14 h-14 rounded-2xl bg-sky-50 dark:bg-sky-950/60 text-sky-600 dark:text-sky-400 flex items-center justify-center mb-3.5 border border-sky-100 dark:border-sky-800">
          <Navigation className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">
          No Train Selected
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5 max-w-xs leading-relaxed">
          Select any train from the live table below or search with a train number to view real-time corridor map and ML predictions.
        </p>
      </div>
    );
  }

  const trainNumber = formatSafeText(trainObj.train_number || trainObj.trainNumber);
  const trainName = formatSafeText(trainObj.train_name || trainObj.trainName);
  const source = formatSafeText(trainObj.source || trainObj.source_station);
  const destination = formatSafeText(trainObj.destination || trainObj.destination_station);
  const currentStation = formatSafeText(
    liveStatus?.current_station_name || liveStatus?.currentStation || 'In Transit'
  );
  const currentCode = liveStatus?.current_station_code || '';
  const nextStation = formatSafeText(
    prediction?.next_station || liveStatus?.next_station_name || 'Approaching stop'
  );
  const nextCode = prediction?.next_station_code || liveStatus?.next_station_code || '';
  const delayMinutes = Number(liveStatus?.current_delay_minutes ?? liveStatus?.delay_minutes ?? 0);
  const speed = liveStatus?.speed_kmh !== undefined ? formatSpeed(liveStatus.speed_kmh) : 'N/A';
  const predictedDelay = prediction?.predicted_delay_minutes;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 p-5 sm:p-6 shadow-xs h-full flex flex-col justify-between">
      <div>
        {/* Top bar: Train number, type badge, and Status */}
        <div className="flex items-start justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono font-black text-lg px-2.5 py-0.5 rounded-lg bg-slate-950 text-white dark:bg-slate-800 dark:text-slate-100 shadow-2xs">
                {trainNumber}
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
                {trainObj.train_type || 'EXPRESS'}
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white mt-1.5 leading-snug">
              {trainName}
            </h3>
          </div>

          <StatusBadge status={liveStatus?.status} delayMinutes={delayMinutes} size="md" />
        </div>

        {/* Route: Source to Destination */}
        <div className="my-3.5 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-1">
            SCHEDULED CORRIDOR
          </div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-800 dark:text-slate-200">
            <span className="truncate">{source}</span>
            <ArrowRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span className="truncate">{destination}</span>
          </div>
        </div>

        {/* 2x2 Telemetry Grid */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          {/* Current Station */}
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/60">
            <div className="flex items-center space-x-1.5 text-slate-400 dark:text-slate-500 mb-1">
              <MapPin className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
              <span className="text-[10px] font-bold uppercase tracking-wider">Current Station</span>
            </div>
            <div className="font-bold text-slate-900 dark:text-white truncate">
              {currentStation}
            </div>
            {currentCode && (
              <span className="text-[11px] font-mono text-slate-400">({currentCode})</span>
            )}
          </div>

          {/* Next Station */}
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/60">
            <div className="flex items-center space-x-1.5 text-slate-400 dark:text-slate-500 mb-1">
              <Navigation className="w-3.5 h-3.5 text-amber-500 shrink-0" />
              <span className="text-[10px] font-bold uppercase tracking-wider">Next Station</span>
            </div>
            <div className="font-bold text-slate-900 dark:text-white truncate">
              {nextStation}
            </div>
            {nextCode && (
              <span className="text-[11px] font-mono text-slate-400">({nextCode})</span>
            )}
          </div>

          {/* Current Delay */}
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/60">
            <div className="flex items-center space-x-1.5 text-slate-400 dark:text-slate-500 mb-1">
              <Clock className="w-3.5 h-3.5 text-sky-500 shrink-0" />
              <span className="text-[10px] font-bold uppercase tracking-wider">Observed Delay</span>
            </div>
            <div
              className={`font-mono font-bold text-sm ${
                delayMinutes > 5
                  ? 'text-amber-600 dark:text-amber-400'
                  : 'text-emerald-600 dark:text-emerald-400'
              }`}
            >
              {formatDelayDisplay(delayMinutes)}
            </div>
          </div>

          {/* Current Speed */}
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/60">
            <div className="flex items-center space-x-1.5 text-slate-400 dark:text-slate-500 mb-1">
              <Gauge className="w-3.5 h-3.5 text-violet-500 shrink-0" />
              <span className="text-[10px] font-bold uppercase tracking-wider">Telemetry Speed</span>
            </div>
            <div className="font-mono font-bold text-sm text-slate-900 dark:text-white">
              {speed}
            </div>
          </div>
        </div>

        {/* Machine Learning Delay Forecast Box (if available) */}
        {predictedDelay !== undefined && (
          <div className="mt-3 p-3 rounded-xl bg-gradient-to-r from-indigo-50/80 via-white to-purple-50/80 dark:from-indigo-950/40 dark:via-slate-900 dark:to-purple-950/40 border border-indigo-200/70 dark:border-indigo-800/60">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-900 dark:text-indigo-300">
                  ML Arrival Forecast
                </span>
              </div>
              <span className="text-[11px] font-mono font-bold text-indigo-700 dark:text-indigo-300">
                {formatDelayDisplay(predictedDelay)}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
              Gradient-boosted model projection considering historical route congestion &amp; recovery.
            </p>
          </div>
        )}
      </div>

      {/* Action buttons */}
      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center gap-2">
        <button
          type="button"
          onClick={onInspectDetails}
          className="flex-1 inline-flex items-center justify-center px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white dark:bg-blue-600 dark:hover:bg-blue-500 text-xs font-semibold shadow-xs transition cursor-pointer space-x-1.5"
        >
          <span>Inspect Full Journey &amp; ML</span>
          <ChevronDown className="w-3.5 h-3.5" />
        </button>

        <button
          type="button"
          onClick={onCenterMap}
          title="Center on route map"
          className="px-3 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-medium transition cursor-pointer border border-slate-200/80 dark:border-slate-700/80"
        >
          <MapPin className="w-4 h-4 text-slate-600 dark:text-slate-300" />
        </button>
      </div>
    </div>
  );
};

export default SelectedTrainPanel;
