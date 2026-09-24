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
    <div className="bg-gradient-to-br from-orange-50 via-white to-amber-50 rounded-[26px] border-2 border-orange-200 shadow-[0_18px_32px_rgba(249,115,22,0.1)] p-5 sm:p-6 flex flex-col justify-between relative overflow-hidden">
      <div className="absolute top-0 right-0 w-36 h-36 bg-orange-200/40 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none" />

      <div>
        <div className="flex items-center justify-between pb-3 border-b border-orange-100 relative z-10 flex-wrap gap-2">
          <div className="flex items-center space-x-2.5 min-w-0">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-orange-500 to-amber-400 text-slate-900 flex items-center justify-center shadow-xs shrink-0">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <span className="text-[11px] font-black text-orange-700 uppercase tracking-[0.18em] block truncate">
                ETA forecast
              </span>
              <span className="text-xs text-slate-500 block truncate">AI travel estimate</span>
            </div>
          </div>

          <div className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-orange-100 text-orange-800 border border-orange-200 shrink-0">
            <Cpu className="w-3 h-3 text-orange-600" />
            <span>AI MODEL</span>
          </div>
        </div>

        <div className="mt-5 relative z-10">
          <div className="flex items-center space-x-2 flex-wrap gap-y-1">
            <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-500">
              Predicted delay
            </span>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-orange-100 text-orange-800 border border-orange-200 shrink-0">
              AI estimate
            </span>
          </div>

          <div className="flex items-baseline space-x-3 mt-2 flex-wrap">
            <span className="text-3xl sm:text-4xl font-black font-mono text-orange-700 tracking-tight break-all">
              {formattedPredictedDelay}
            </span>
          </div>

          <div className="mt-3 flex items-start space-x-1.5 text-[11px] text-slate-500 bg-white/70 p-2.5 rounded-xl border border-orange-100 leading-relaxed">
            <Info className="w-3.5 h-3.5 text-orange-500 shrink-0 mt-0.5" />
            <span>
              This is a route-based prediction from the live model and can vary with operational conditions.
            </span>
          </div>
        </div>
      </div>

      <div className="mt-5 pt-3.5 border-t border-orange-100 relative z-10">
        {hasComparison ? (
          <div className="bg-white/90 backdrop-blur-xs p-3 rounded-xl border border-orange-100">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs">
              <div className="text-slate-600">
                <span className="font-semibold text-slate-700 uppercase">Current:</span>{' '}
                <span className="font-mono font-bold">{formatDelayDisplay(liveDelayMinutes)}</span>
              </div>
              <div className="text-orange-900">
                <span className="font-semibold text-orange-800 uppercase">Forecast:</span>{' '}
                <span className="font-mono font-bold text-orange-700">{formattedPredictedDelay}</span>
              </div>
            </div>

            <div className="mt-2 pt-2 border-t border-slate-100 flex items-start space-x-1.5 text-xs font-medium">
              {delayTrend === 'recovering' && (
                <>
                  <TrendingDown className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span className="text-emerald-700">
                    Model suggests ~{Math.abs(deltaMinutes)} min recovery
                  </span>
                </>
              )}
              {delayTrend === 'increasing' && (
                <>
                  <TrendingUp className="w-4 h-4 text-amber-600 shrink-0" />
                  <span className="text-amber-700">
                    Model estimates +{deltaMinutes} min extra delay
                  </span>
                </>
              )}
              {delayTrend === 'same' && (
                <>
                  <Minus className="w-4 h-4 text-slate-500 shrink-0" />
                  <span className="text-slate-600">
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
