import React from 'react';
import { MapPin, Clock, Gauge, Radio, Hash } from 'lucide-react';
import { formatSafeText, formatDelayDisplay, formatSpeed } from '../utils/formatters';

/**
 * Live Status Card: Displays current station, code, sequence, speed, and live delay.
 */
export const CurrentStatusCard = ({ liveStatus }) => {
  const stationName = formatSafeText(liveStatus?.current_station_name);
  const stationCode = formatSafeText(liveStatus?.current_station_code);
  const delayMinutes = liveStatus?.current_delay_minutes;
  const speed = liveStatus?.speed_kmh;
  const sequence = liveStatus?.current_sequence;

  const formattedDelay = formatDelayDisplay(delayMinutes);
  const formattedSpeed = formatSpeed(speed);
  const formattedSequence =
    sequence !== null && sequence !== undefined && !Number.isNaN(Number(sequence))
      ? `Stop #${sequence}`
      : 'Not available';

  const isDelayed = typeof delayMinutes === 'number' && delayMinutes > 5;
  const isOnTime = typeof delayMinutes === 'number' && delayMinutes <= 5 && delayMinutes >= 0;

  return (
    <div className="bg-white rounded-[26px] border border-slate-200 shadow-[0_18px_32px_rgba(15,23,42,0.08)] p-5 sm:p-6 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 flex-wrap gap-2">
          <div className="flex items-center space-x-2.5 min-w-0">
            <div className="w-9 h-9 rounded-xl bg-sky-100 text-sky-700 flex items-center justify-center shrink-0">
              <MapPin className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-[0.18em] block truncate">
                Current station
              </span>
              <span className="text-xs text-slate-400 block truncate">Live signal</span>
            </div>
          </div>

          <div className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-700 border border-emerald-200 shrink-0">
            <Radio className="w-3 h-3 text-emerald-600 animate-pulse" />
            <span>LIVE</span>
          </div>
        </div>

        <div className="mt-4">
          <div className="flex items-baseline space-x-2.5 flex-wrap gap-y-1">
            <h3 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight break-words">
              {stationName}
            </h3>
            {stationCode !== 'Not available' && (
              <span className="px-2.5 py-0.5 rounded-lg bg-slate-100 text-slate-800 text-xs font-mono font-bold border border-slate-200 shrink-0">
                {stationCode}
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-1">Most recent railway checkpoint reported</p>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
          <div className="flex items-center space-x-1 text-[10px] font-bold text-slate-500 uppercase tracking-[0.15em] mb-1">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>Delay</span>
          </div>
          <div
            className={`text-lg font-black font-mono ${
              isDelayed ? 'text-amber-600' : isOnTime ? 'text-emerald-600' : 'text-slate-900'
            }`}
          >
            {formattedDelay}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Current delay</div>
        </div>

        <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
          <div className="flex items-center space-x-1 text-[10px] font-bold text-slate-500 uppercase tracking-[0.15em] mb-1">
            <Gauge className="w-3.5 h-3.5 text-slate-400" />
            <span>Speed</span>
          </div>
          <div className="text-lg font-black font-mono text-slate-900">
            {formattedSpeed}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Current speed</div>
        </div>

        <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
          <div className="flex items-center space-x-1 text-[10px] font-bold text-slate-500 uppercase tracking-[0.15em] mb-1">
            <Hash className="w-3.5 h-3.5 text-slate-400" />
            <span>Stop</span>
          </div>
          <div className="text-lg font-black font-mono text-slate-900">
            {formattedSequence}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Route sequence</div>
        </div>
      </div>
    </div>
  );
};

export default CurrentStatusCard;
