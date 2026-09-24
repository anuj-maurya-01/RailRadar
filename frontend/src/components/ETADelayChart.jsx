import React from 'react';
import {
  Clock,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Minus,
  CalendarClock,
  BarChart3,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react';
import {
  formatSafeText,
  formatDelayDisplay,
  formatTimeDisplay,
} from '../utils/formatters';

/**
 * ETADelayChart Component:
 * Clean, accessible visual comparison between:
 * 1. Scheduled arrival/departure time
 * 2. ML-predicted expected arrival/departure time
 * 3. Delay in minutes (Live Delay vs ML Predicted Delay)
 */
export const ETADelayChart = ({ trainData }) => {
  if (!trainData) return null;

  const liveStatus = trainData.live_status || {};
  const prediction = trainData.prediction || {};
  const train = trainData.train || {};
  const route = trainData.route || {};

  // Extract timings
  const nextStationName = formatSafeText(prediction.next_station, 'Next Station');
  const nextStationCode = formatSafeText(prediction.next_station_code);

  const schedArr = formatTimeDisplay(prediction.scheduled_arrival);
  const expArr = formatTimeDisplay(prediction.expected_arrival);
  const schedDep = formatTimeDisplay(prediction.scheduled_departure);
  const expDep = formatTimeDisplay(prediction.expected_departure);

  const destName = formatSafeText(train.destination, 'Terminus');
  const destEta = formatTimeDisplay(prediction.destination_eta);

  // Extract delays
  const liveDelay = liveStatus.current_delay_minutes;
  const predDelay = prediction.predicted_delay_minutes;

  const hasLiveDelay = typeof liveDelay === 'number' && !Number.isNaN(liveDelay);
  const hasPredDelay = typeof predDelay === 'number' && !Number.isNaN(predDelay);

  // Compute delay metrics & variance
  let deltaDelay = 0;
  let delayTrend = 'same';

  if (hasLiveDelay && hasPredDelay) {
    deltaDelay = Math.round((predDelay - liveDelay) * 10) / 10;
    if (deltaDelay < -1) {
      delayTrend = 'recovering';
    } else if (deltaDelay > 1) {
      delayTrend = 'increasing';
    }
  }

  // Relative scaling for comparison bars
  const highestVal = Math.max(
    hasLiveDelay ? Math.max(0, liveDelay) : 0,
    hasPredDelay ? Math.max(0, predDelay) : 0,
    30
  );
  const maxScale = Math.ceil(highestVal * 1.2);

  const liveBarWidth = hasLiveDelay
    ? Math.min(100, Math.max(8, (Math.max(0, liveDelay) / maxScale) * 100))
    : 0;
  const predBarWidth = hasPredDelay
    ? Math.min(100, Math.max(8, (Math.max(0, predDelay) / maxScale) * 100))
    : 0;

  // Destination scheduled arrival from last station in route if present
  let destSchedArr = 'Not available';
  if (Array.isArray(route.stations) && route.stations.length > 0) {
    const lastStop = route.stations[route.stations.length - 1];
    if (lastStop && (lastStop.scheduledArrival || lastStop.scheduled_arrival)) {
      destSchedArr = formatTimeDisplay(lastStop.scheduledArrival || lastStop.scheduled_arrival);
    }
  }

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
      {/* Section Header */}
      <div className="px-5 sm:px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-3 bg-slate-50 dark:bg-slate-850">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center shadow-xs">
            <BarChart3 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
              ETA &amp; Delay Variance Analysis
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Timetable Schedule vs. ML Arrival Forecast &amp; Delay Evolution
            </p>
          </div>
        </div>

        {/* Indicator Badges */}
        <div className="flex flex-wrap items-center gap-2 text-xs font-medium">
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
            <span className="w-2 h-2 rounded-full bg-slate-500"></span>
            <span>Scheduled Baseline</span>
          </div>
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 font-semibold">
            <span className="w-2 h-2 rounded-full bg-indigo-600"></span>
            <span>ML Expected Forecast</span>
          </div>
        </div>
      </div>

      <div className="p-5 sm:p-6 lg:p-7 space-y-6">
        {/* 1. Next Station Arrival & Departure Shift Visualizer */}
        <div className="bg-slate-50/80 dark:bg-slate-800/40 rounded-xl p-4 sm:p-5 border border-slate-200/80 dark:border-slate-800">
          <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-200/60 dark:border-slate-800">
            <div>
              <span className="text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">
                Upcoming Stop Timing Shift
              </span>
              <div className="flex items-baseline space-x-2 mt-0.5">
                <span className="text-base font-bold text-slate-900 dark:text-white">
                  {nextStationName}
                </span>
                {nextStationCode !== 'Not available' && (
                  <span className="px-1.5 py-0.2 rounded bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-mono font-bold">
                    {nextStationCode}
                  </span>
                )}
              </div>
            </div>

            {hasPredDelay && (
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-indigo-100 dark:bg-indigo-950/60 text-indigo-800 dark:text-indigo-300 text-xs font-mono font-bold">
                <Sparkles className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 shrink-0" />
                <span>Shift: {formatDelayDisplay(predDelay)}</span>
              </div>
            )}
          </div>

          {/* Time Offset Differential Visualization */}
          <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Arrival Differential Bar */}
            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200/90 dark:border-slate-800 shadow-xs">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-500 dark:text-slate-400 pb-2">
                <div className="flex items-center space-x-1.5">
                  <CalendarClock className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  <span className="uppercase tracking-wider">Arrival Comparison</span>
                </div>
                <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500">Timetable &rarr; ML Expected</span>
              </div>

              {/* Time Nodes */}
              <div className="mt-3 flex items-center justify-between font-mono gap-2">
                <div className="shrink-0">
                  <div className="text-[10px] font-sans font-semibold text-slate-400 dark:text-slate-500 uppercase">
                    Scheduled
                  </div>
                  <div className="text-sm sm:text-base md:text-lg font-bold text-slate-800 dark:text-slate-200 mt-0.5">
                    {schedArr}
                  </div>
                </div>

                <div className="flex-1 min-w-0 mx-1 sm:mx-3 flex flex-col items-center">
                  <div className="text-[10px] sm:text-[11px] font-sans font-bold text-amber-600 dark:text-amber-400 truncate max-w-full">
                    {hasPredDelay ? formatDelayDisplay(predDelay) : 'Delay shift'}
                  </div>
                  <div className="w-full relative flex items-center my-1">
                    <div className="w-2 h-2 rounded-full bg-slate-400 shrink-0" />
                    <div className="flex-1 h-1.5 bg-gradient-to-r from-slate-300 via-amber-400 to-indigo-500 rounded-full mx-1 min-w-[16px]" />
                    <ArrowRight className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 shrink-0 -ml-1" />
                  </div>
                  <div className="text-[9px] sm:text-[10px] font-sans text-slate-400 dark:text-slate-500 truncate max-w-full">
                    ML delay extension
                  </div>
                </div>

                <div className="shrink-0 text-right">
                  <div className="text-[10px] font-sans font-bold text-indigo-600 dark:text-indigo-400 uppercase">
                    ML Expected
                  </div>
                  <div className="text-sm sm:text-base md:text-lg font-extrabold text-indigo-700 dark:text-indigo-300 mt-0.5">
                    {expArr}
                  </div>
                </div>
              </div>
            </div>

            {/* Departure Differential Bar */}
            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200/90 dark:border-slate-800 shadow-xs">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-500 dark:text-slate-400 pb-2">
                <div className="flex items-center space-x-1.5">
                  <Clock className="w-4 h-4 text-slate-500 dark:text-slate-400" />
                  <span className="uppercase tracking-wider">Departure Comparison</span>
                </div>
                <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500">Timetable &rarr; ML Expected</span>
              </div>

              {/* Time Nodes */}
              <div className="mt-3 flex items-center justify-between font-mono gap-2">
                <div className="shrink-0">
                  <div className="text-[10px] font-sans font-semibold text-slate-400 dark:text-slate-500 uppercase">
                    Scheduled
                  </div>
                  <div className="text-sm sm:text-base md:text-lg font-bold text-slate-800 dark:text-slate-200 mt-0.5">
                    {schedDep}
                  </div>
                </div>

                <div className="flex-1 min-w-0 mx-1 sm:mx-3 flex flex-col items-center">
                  <div className="text-[10px] sm:text-[11px] font-sans font-bold text-amber-600 dark:text-amber-400 truncate max-w-full">
                    {hasPredDelay ? formatDelayDisplay(predDelay) : 'Delay shift'}
                  </div>
                  <div className="w-full relative flex items-center my-1">
                    <div className="w-2 h-2 rounded-full bg-slate-400 shrink-0" />
                    <div className="flex-1 h-1.5 bg-gradient-to-r from-slate-300 via-amber-400 to-indigo-500 rounded-full mx-1 min-w-[16px]" />
                    <ArrowRight className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 shrink-0 -ml-1" />
                  </div>
                  <div className="text-[9px] sm:text-[10px] font-sans text-slate-400 dark:text-slate-500 truncate max-w-full">
                    Projected departure
                  </div>
                </div>

                <div className="shrink-0 text-right">
                  <div className="text-[10px] font-sans font-bold text-indigo-600 dark:text-indigo-400 uppercase">
                    ML Expected
                  </div>
                  <div className="text-sm sm:text-base md:text-lg font-extrabold text-indigo-700 dark:text-indigo-300 mt-0.5">
                    {expDep}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 2. Comparative Delay Bars: LIVE DELAY vs ML PREDICTED DELAY */}
        <div className="bg-white dark:bg-slate-900 rounded-xl p-5 border border-slate-200 dark:border-slate-800 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h4 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                Delay Magnitude Comparison
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Observed live ground delay vs. machine-learning predicted arrival delay (in minutes)
              </p>
            </div>

            {/* Delay Delta Trend Callout */}
            {hasLiveDelay && hasPredDelay && (
              <div className="flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                {delayTrend === 'recovering' && (
                  <>
                    <TrendingDown className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
                    <span className="text-emerald-700 dark:text-emerald-400 font-bold">
                      {Math.abs(deltaDelay)} min delay recovery projected
                    </span>
                  </>
                )}
                {delayTrend === 'increasing' && (
                  <>
                    <TrendingUp className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
                    <span className="text-amber-700 dark:text-amber-400 font-bold">
                      +{deltaDelay} min additional congestion delay projected
                    </span>
                  </>
                )}
                {delayTrend === 'same' && (
                  <>
                    <Minus className="w-4 h-4 text-slate-500 dark:text-slate-400 shrink-0" />
                    <span className="text-slate-600 dark:text-slate-300 font-bold">
                      Delay projected to hold steady
                    </span>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Side-by-Side Visual Bars */}
          <div className="mt-5 space-y-4">
            {/* Live Delay Bar */}
            <div>
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  LIVE DELAY (Ground Telemetry)
                </span>
                <span className="font-mono font-extrabold text-amber-600 dark:text-amber-400 text-sm">
                  {formatDelayDisplay(liveDelay)}
                </span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-3.5 overflow-hidden p-0.5 border border-slate-200/60 dark:border-slate-700">
                <div
                  className="bg-amber-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${liveBarWidth}%` }}
                  title={`Live Delay: ${liveDelay} min`}
                />
              </div>
            </div>

            {/* ML Predicted Delay Bar */}
            <div>
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-bold text-indigo-700 dark:text-indigo-400 uppercase tracking-wider flex items-center space-x-1">
                  <span>ML PREDICTED DELAY (AI Model)</span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-indigo-100 dark:bg-indigo-950/60 text-indigo-800 dark:text-indigo-300 font-normal">
                    HistGradientBoosting
                  </span>
                </span>
                <span className="font-mono font-extrabold text-indigo-700 dark:text-indigo-400 text-sm">
                  {formatDelayDisplay(predDelay)}
                </span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-3.5 overflow-hidden p-0.5 border border-slate-200/60 dark:border-slate-700">
                <div
                  className="bg-indigo-600 h-full rounded-full transition-all duration-500"
                  style={{ width: `${predBarWidth}%` }}
                  title={`ML Predicted Delay: ${predDelay} min`}
                />
              </div>
            </div>
          </div>
        </div>

        {/* 3. Journey Terminus ETA Overview Card */}
        <div className="bg-gradient-to-r from-slate-50 via-emerald-50/30 to-blue-50/20 dark:from-slate-850 dark:via-emerald-950/20 dark:to-slate-850 p-4 sm:p-5 rounded-xl border border-slate-200 dark:border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1 min-w-0">
            <div className="text-[11px] font-bold text-emerald-800 dark:text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <span>Terminus Destination ETA Projection</span>
            </div>
            <div className="text-base sm:text-lg font-extrabold text-slate-900 dark:text-white break-words">
              {destName}
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Arrival time adjusted by cumulative route recovery and gradient-boosted delay projection.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 font-mono">
            {destSchedArr !== 'Not available' && (
              <div className="px-3.5 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-center flex-1 sm:flex-initial">
                <div className="text-[10px] font-sans font-semibold text-slate-400 dark:text-slate-500 uppercase">
                  Scheduled Terminus
                </div>
                <div className="text-base font-bold text-slate-800 dark:text-slate-200 mt-0.5">
                  {destSchedArr}
                </div>
              </div>
            )}

            <div className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-center shadow-xs flex-1 sm:flex-initial">
              <div className="text-[10px] font-sans font-bold uppercase tracking-wider text-emerald-100">
                Destination ETA
              </div>
              <div className="text-lg font-black mt-0.5">
                {destEta}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ETADelayChart;
