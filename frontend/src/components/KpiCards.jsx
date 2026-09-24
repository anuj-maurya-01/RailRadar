import React from 'react';
import { Train, CheckCircle2, Clock, AlertOctagon, TrendingUp, Radio } from 'lucide-react';

/**
 * 4 Clean KPI Cards for Railway Intelligence Dashboard
 * Grid layout: 4 in 1 row (Desktop) -> 2x2 (Tablet) -> 1 column (Mobile)
 * Values dynamically calculated from actual application data.
 */
export const KpiCards = ({
  stats = {},
  activeFilter = 'all',
  onSelectFilter = () => {},
  loading = false,
}) => {
  const activeCount = stats.active_trains ?? 0;
  const onTimeCount = stats.on_time ?? 0;
  const delayedCount = stats.delayed ?? 0;
  const cancelledCount = stats.cancelled ?? 0;

  const cards = [
    {
      id: 'all',
      title: 'ACTIVE TRAINS',
      count: activeCount,
      icon: Train,
      iconBg: 'bg-sky-500/10 text-sky-600 dark:bg-sky-500/20 dark:text-sky-400',
      badge: 'Live Network',
      badgeBg: 'bg-sky-50 text-sky-700 dark:bg-sky-950/60 dark:text-sky-300 border-sky-200 dark:border-sky-800',
      accent: 'border-l-sky-500',
    },
    {
      id: 'on_time',
      title: 'ON TIME',
      count: onTimeCount,
      icon: CheckCircle2,
      iconBg: 'bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400',
      badge: 'Optimal',
      badgeBg: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
      accent: 'border-l-emerald-500',
    },
    {
      id: 'delayed',
      title: 'DELAYED',
      count: delayedCount,
      icon: Clock,
      iconBg: 'bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400',
      badge: '> 5m Delay',
      badgeBg: 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-800',
      accent: 'border-l-amber-500',
    },
    {
      id: 'cancelled',
      title: 'CANCELLED',
      count: cancelledCount,
      icon: AlertOctagon,
      iconBg: 'bg-rose-500/10 text-rose-600 dark:bg-rose-500/20 dark:text-rose-400',
      badge: 'Zero Impact',
      badgeBg: 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border-rose-200 dark:border-rose-800',
      accent: 'border-l-rose-500',
    },
  ];

  if (loading) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="animate-pulse bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/80 p-3.5 sm:p-5 shadow-xs h-28 sm:h-32 flex flex-col justify-between"
          >
            <div className="flex items-center justify-between">
              <div className="w-16 sm:w-24 h-4 bg-slate-200 dark:bg-slate-700 rounded" />
              <div className="w-7 h-7 sm:w-8 sm:h-8 bg-slate-200 dark:bg-slate-700 rounded-xl" />
            </div>
            <div className="w-12 sm:w-16 h-7 sm:h-8 bg-slate-200 dark:bg-slate-700 rounded" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        const isSelected = activeFilter === card.id;

        return (
          <button
            key={card.id}
            type="button"
            onClick={() => onSelectFilter(card.id)}
            className={`text-left rounded-2xl border transition-all duration-200 p-3.5 sm:p-5 shadow-xs cursor-pointer relative overflow-hidden group border-l-4 ${card.accent} ${
              isSelected
                ? 'bg-slate-50 dark:bg-slate-800 border-slate-300 dark:border-slate-600 shadow-md ring-2 ring-blue-500/20'
                : 'bg-white dark:bg-slate-900 border-slate-200/90 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 hover:shadow-sm'
            }`}
          >
            <div className="flex items-start justify-between gap-1">
              <div className="min-w-0">
                <p className="text-[10px] sm:text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 truncate">
                  {card.title}
                </p>
                <div className="flex items-baseline space-x-1.5 sm:space-x-2 mt-1">
                  <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white font-mono tracking-tight">
                    {card.count}
                  </span>
                </div>
              </div>

              <div
                className={`w-8 h-8 sm:w-10 sm:h-10 rounded-xl flex items-center justify-center shrink-0 transition-transform group-hover:scale-105 ${card.iconBg}`}
              >
                <Icon className="w-4 h-4 sm:w-5 sm:h-5" />
              </div>
            </div>

            <div className="mt-2.5 sm:mt-3 flex items-center justify-between text-xs pt-2 sm:pt-2.5 border-t border-slate-100 dark:border-slate-800">
              <span className={`inline-flex items-center px-1.5 sm:px-2 py-0.5 rounded-full text-[9px] sm:text-[10px] font-semibold border ${card.badgeBg}`}>
                {card.badge}
              </span>
              <span className="text-[10px] sm:text-[11px] text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors hidden sm:inline">
                {isSelected ? 'Filtering • Reset' : 'Filter table →'}
              </span>
            </div>
          </button>
        );
      })}
    </div>
  );

};

export default KpiCards;
