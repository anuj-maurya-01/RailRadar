import React, { useState } from 'react';
import { AlertTriangle, Clock, ArrowRight, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { formatDelayDisplay } from '../utils/formatters';

/**
 * Compact Live Railway Alerts Component
 * Shows real alerts derived from active delayed trains. Never fabricates fake alerts.
 */
export const AlertsCard = ({
  alerts = [],
  onSelectTrain = () => {},
}) => {
  const [showAll, setShowAll] = useState(false);
  const visibleAlerts = showAll ? alerts : alerts.slice(0, 3);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 p-4 sm:p-5 shadow-xs">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center">
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              Live Network Alerts
            </h3>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Active telemetry anomalies &amp; delay notices
            </p>
          </div>
        </div>

        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border border-amber-300/40">
          {alerts.length} Active
        </span>
      </div>

      {alerts.length === 0 ? (
        <div className="py-6 text-center text-xs text-slate-500 dark:text-slate-400 flex flex-col items-center justify-center">
          <CheckCircle2 className="w-8 h-8 text-emerald-500 mb-2" />
          <span className="font-semibold text-slate-700 dark:text-slate-300">All Corridors Operating Smoothly</span>
          <span className="text-[11px] mt-0.5">No critical delay notices reported on tracked lines.</span>
        </div>
      ) : (
        <div className="divide-y divide-slate-100 dark:divide-slate-800/80 mt-1">
          {visibleAlerts.map((alert) => {
            const isCritical = alert.severity === 'alert';

            return (
              <div
                key={alert.id}
                onClick={() => onSelectTrain(alert.train_number)}
                className="py-3 group cursor-pointer flex items-start justify-between gap-3 hover:bg-slate-50/80 dark:hover:bg-slate-800/40 px-2 -mx-2 rounded-xl transition"
              >
                <div className="flex items-start space-x-2.5 min-w-0">
                  <div
                    className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                      isCritical ? 'bg-rose-500 animate-ping' : 'bg-amber-500'
                    }`}
                  />
                  <div className="min-w-0">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-xs text-slate-900 dark:text-white">
                        #{alert.train_number}
                      </span>
                      <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 truncate">
                        {alert.train_name}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5 leading-snug">
                      {alert.message}
                    </p>
                    <div className="flex items-center space-x-2 text-[10px] text-slate-400 dark:text-slate-500 mt-1">
                      <span>{alert.location}</span>
                      <span>•</span>
                      <span>{alert.timestamp}</span>
                    </div>
                  </div>
                </div>

                <button
                  type="button"
                  className="shrink-0 p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/40 text-slate-500 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition"
                  title="Inspect train on map"
                >
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {alerts.length > 3 && (
        <div className="pt-2 border-t border-slate-100 dark:border-slate-800 text-center">
          <button
            type="button"
            onClick={() => setShowAll(!showAll)}
            className="text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline cursor-pointer"
          >
            {showAll ? 'Show fewer alerts ↑' : `View all ${alerts.length} alerts →`}
          </button>
        </div>
      )}
    </div>
  );
};

export default AlertsCard;
