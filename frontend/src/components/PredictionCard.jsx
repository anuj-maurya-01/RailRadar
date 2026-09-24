import React from 'react';
import { Sparkles, TrendingDown, TrendingUp, Minus, Cpu, Info } from 'lucide-react';
import { formatDelayDisplay } from '../utils/formatters';

/**
 * ML Prediction Card: Displays ML Predicted Delay with explicit "AI/ML estimated delay"
 * label, model disclaimer, and live delay comparison.
 */
export const PredictionCard = ({ prediction, liveDelayMinutes }) => {
  const predictedDelay = prediction?.predicted_delay_minutes;
  const formattedPredictedDelay = formatDelayDisplay(predictedDelay);

  // Compute comparison with current live delay if both are numbers
  const hasComparison =
    typeof predictedDelay === 'number' &&
    typeof liveDelayMinutes === 'number' &&
    !Number.isNaN(predictedDelay) &&
    !Number.isNaN(liveDelayMinutes);

  let deltaMinutes = 0;
  let delayTrend = 'same'; // 'recovering', 'increasing', 'same'

  if (hasComparison) {
    deltaMinutes = Math.round((predictedDelay - liveDelayMinutes) * 10) / 10;
    if (deltaMinutes < -1) {
      delayTrend = 'recovering';
    } else if (deltaMinutes > 1) {
      delayTrend = 'increasing';
    }
  }

  return (
    <div className="bg-gradient-to-br from-indigo-50/70 via-white to-purple-50/70 dark:from-indigo-950/40 dark:via-slate-900 dark:to-purple-950/40 rounded-2xl border border-indigo-200/80 dark:border-indigo-800/80 shadow-xs p-5 sm:p-6 flex flex-col justify-between relative overflow-hidden">
      <div className="absolute top-0 right-0 w-36 h-36 bg-indigo-200/30 dark:bg-indigo-700/10 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none" />

      <div>
        <div className="flex items-center justify-between pb-3 border-b border-indigo-100 dark:border-indigo-900/60 relative z-10 flex-wrap gap-2">
          <div className="flex items-center space-x-2.5 min-w-0">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 text-white flex items-center justify-center shadow-xs shrink-0">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <span className="text-[11px] font-bold text-indigo-700 dark:text-indigo-300 uppercase tracking-wider block truncate">
                ETA Forecast
              </span>
              <span className="text-xs text-slate-400 dark:text-slate-500 block truncate">Machine Learning Estimate</span>
            </div>
          </div>

          <div className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-100 dark:bg-indigo-950/80 text-indigo-800 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 shrink-0">
            <Cpu className="w-3 h-3 text-indigo-600 dark:text-indigo-400" />
            <span>ML MODEL</span>
          </div>
        </div>

        <div className="mt-5 relative z-10">
          <div className="flex items-center space-x-2 flex-wrap gap-y-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              Predicted Delay
            </span>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-100 dark:bg-indigo-950/80 text-indigo-800 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 shrink-0">
              HistGradientBoosting
            </span>
          </div>

          <div className="flex items-baseline space-x-3 mt-2 flex-wrap">
            <span className="text-3xl sm:text-4xl font-black font-mono text-indigo-700 dark:text-indigo-300 tracking-tight break-all">
              {formattedPredictedDelay}
            </span>
          </div>

          <div className="mt-3 flex items-start space-x-1.5 text-[11px] text-slate-500 dark:text-slate-400 bg-white/70 dark:bg-slate-800/60 p-2.5 rounded-xl border border-indigo-100 dark:border-indigo-900/60 leading-relaxed">
            <Info className="w-3.5 h-3.5 text-indigo-500 shrink-0 mt-0.5" />
            <span>
              Trained on 12 operational route features including timetable variance, rush-hour dynamics, and segment progress.
            </span>
          </div>
        </div>
      </div>

      <div className="mt-5 pt-3.5 border-t border-indigo-100 dark:border-indigo-900/60 relative z-10">
        {hasComparison ? (
          <div className="bg-white/90 dark:bg-slate-800/80 backdrop-blur-xs p-3 rounded-xl border border-indigo-100 dark:border-indigo-900/60">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs">
              <div className="text-slate-600 dark:text-slate-300">
                <span className="font-semibold text-slate-500 dark:text-slate-400 uppercase">Live:</span>{' '}
                <span className="font-mono font-bold">{formatDelayDisplay(liveDelayMinutes)}</span>
              </div>
              <div className="text-indigo-900 dark:text-indigo-200">
                <span className="font-semibold text-indigo-600 dark:text-indigo-400 uppercase">Forecast:</span>{' '}
                <span className="font-mono font-bold text-indigo-700 dark:text-indigo-300">{formattedPredictedDelay}</span>
              </div>
            </div>

            <div className="mt-2 pt-2 border-t border-slate-100 dark:border-slate-700 flex items-start space-x-1.5 text-xs font-medium">
              {delayTrend === 'recovering' && (
                <>
                  <TrendingDown className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
                  <span className="text-emerald-700 dark:text-emerald-300">
                    Model suggests ~{Math.abs(deltaMinutes)} min delay recovery
                  </span>
                </>
              )}
              {delayTrend === 'increasing' && (
                <>
                  <TrendingUp className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
                  <span className="text-amber-700 dark:text-amber-300">
                    Model estimates +{deltaMinutes} min extra delay
                  </span>
                </>
              )}
              {delayTrend === 'same' && (
                <>
                  <Minus className="w-4 h-4 text-slate-400 shrink-0" />
                  <span className="text-slate-500 dark:text-slate-400">
                    Delay expected to remain stable
                  </span>
                </>
              )}
            </div>
          </div>
        ) : (
          <div className="text-xs text-slate-400 italic">
            Comparison data unavailable for this segment.
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictionCard;
