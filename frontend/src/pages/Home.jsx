import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Loader2,
  AlertCircle,
  Train,
  ShieldCheck,
  Compass,
  Sparkles,
  RefreshCw,
  Radio,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  MapPin,
  Clock,
  Layers,
} from 'lucide-react';
import { getTrain, getLiveSummary } from '../services/api';
import Header from '../components/Header';
import TrainSearch from '../components/TrainSearch';
import KpiCards from '../components/KpiCards';
import LiveIndicator from '../components/LiveIndicator';
import SelectedTrainPanel from '../components/SelectedTrainPanel';
import TrainTable from '../components/TrainTable';
import AlertsCard from '../components/AlertsCard';
import TrainMap from '../components/TrainMap';
import TrainOverview from '../components/TrainOverview';
import CurrentStatusCard from '../components/CurrentStatusCard';
import PredictionCard from '../components/PredictionCard';
import NextStationCard from '../components/NextStationCard';
import DestinationCard from '../components/DestinationCard';
import ETADelayChart from '../components/ETADelayChart';
import RouteTimeline from '../components/RouteTimeline';
import { formatDelayDisplay } from '../utils/formatters';

const REFRESH_INTERVAL_MS = 30000; // 30s live telemetry refresh

export const Home = ({
  activeTab = 'dashboard',
  setActiveTab = () => {},
  setAlertCount = () => {},
  searchInputRef = null,
}) => {
  // Search & Selected Train State
  const [trainNumber, setTrainNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [trainData, setTrainData] = useState(null);
  const [selectedSummary, setSelectedSummary] = useState(null);

  // Live Summary & Table State
  const [summaryData, setSummaryData] = useState({
    stats: { active_trains: 0, on_time: 0, delayed: 0, cancelled: 0, total_tracked: 0 },
    trains: [],
    alerts: [],
  });
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [tableFilter, setTableFilter] = useState('all');

  // Auto-Refresh & Timing State
  const [activeTrainNumber, setActiveTrainNumber] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [timeAgo, setTimeAgo] = useState('Just now');

  // Deep Details Section Toggle
  const [deepDetailsExpanded, setDeepDetailsExpanded] = useState(true);

  // Refs for tracking active lifecycle and scroll targets
  const currentRequestIdRef = useRef(0);
  const pollingTimerRef = useRef(null);
  const activeTrainRef = useRef(null);
  const isRefreshingRef = useRef(false);

  const mapSectionRef = useRef(null);
  const tableSectionRef = useRef(null);
  const alertsSectionRef = useRef(null);
  const deepDetailsRef = useRef(null);

  // 1. Fetch Live Summary on Initial Mount
  const loadLiveSummary = useCallback(async () => {
    try {
      setSummaryLoading(true);
      const data = await getLiveSummary();
      if (data && data.success) {
        setSummaryData({
          stats: data.stats || {},
          trains: data.trains || [],
          alerts: data.alerts || [],
        });
        if (data.alerts && Array.isArray(data.alerts)) {
          setAlertCount(data.alerts.length);
        }
        setLastUpdated(new Date());
        setTimeAgo('Just now');
      }
    } catch (err) {
      console.warn('Initial live summary fetch failed:', err.message);
    } finally {
      setSummaryLoading(false);
    }
  }, [setAlertCount]);

  useEffect(() => {
    loadLiveSummary();
  }, [loadLiveSummary]);

  // 2. Tab Navigation Actions
  useEffect(() => {
    if (activeTab === 'live_trains' && tableSectionRef.current) {
      tableSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if (activeTab === 'alerts' && alertsSectionRef.current) {
      alertsSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if (activeTab === 'delays') {
      setTableFilter('delayed');
      if (tableSectionRef.current) {
        tableSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } else if (activeTab === 'stations' && deepDetailsRef.current) {
      setDeepDetailsExpanded(true);
      deepDetailsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [activeTab]);

  // 3. Update Relative Elapsed Time Every 5 Seconds
  useEffect(() => {
    if (!lastUpdated) return;

    const timer = setInterval(() => {
      const diffSec = Math.max(0, Math.floor((Date.now() - lastUpdated.getTime()) / 1000));
      if (diffSec < 5) {
        setTimeAgo('Just now');
      } else if (diffSec < 60) {
        setTimeAgo(`${diffSec}s ago`);
      } else {
        const diffMin = Math.floor(diffSec / 60);
        setTimeAgo(`${diffMin}m ago`);
      }
    }, 5000);

    return () => clearInterval(timer);
  }, [lastUpdated]);

  // 4. Background Refresh Function
  const refreshTrainData = useCallback(async () => {
    const targetTrain = activeTrainRef.current;
    if (isRefreshingRef.current) return;

    isRefreshingRef.current = true;
    setIsRefreshing(true);
    const reqId = ++currentRequestIdRef.current;

    try {
      // Parallel refresh: active train (if selected) + live summary
      const promises = [getLiveSummary()];
      if (targetTrain) {
        promises.push(getTrain(targetTrain));
      }

      const results = await Promise.allSettled(promises);
      const summaryRes = results[0];
      const trainRes = results[1];

      if (summaryRes.status === 'fulfilled' && summaryRes.value?.success) {
        setSummaryData({
          stats: summaryRes.value.stats || {},
          trains: summaryRes.value.trains || [],
          alerts: summaryRes.value.alerts || [],
        });
        if (summaryRes.value.alerts) {
          setAlertCount(summaryRes.value.alerts.length);
        }
      }

      if (
        trainRes &&
        trainRes.status === 'fulfilled' &&
        reqId === currentRequestIdRef.current &&
        activeTrainRef.current === targetTrain
      ) {
        setTrainData(trainRes.value);
      }

      setLastUpdated(new Date());
      setTimeAgo('Just now');
      setRefreshError(null);
    } catch (err) {
      if (reqId === currentRequestIdRef.current) {
        console.warn(`[AutoRefresh] Update hiccup:`, err.message);
        setRefreshError('Temporary telemetry update hiccup. Retrying in 30s...');
      }
    } finally {
      if (reqId === currentRequestIdRef.current) {
        isRefreshingRef.current = false;
        setIsRefreshing(false);
      }
    }
  }, [setAlertCount]);

  // Set up 30s polling
  useEffect(() => {
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current);
    }

    pollingTimerRef.current = setInterval(() => {
      refreshTrainData();
    }, REFRESH_INTERVAL_MS);

    return () => {
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
      }
    };
  }, [refreshTrainData]);

  // 5. Execute Train Search / Selection
  const executeSearch = async (numToSearch, summaryObj = null) => {
    const cleanNumber = String(numToSearch || '').trim();

    if (!cleanNumber) {
      setError('Please enter a train number.');
      setTrainData(null);
      setActiveTrainNumber(null);
      activeTrainRef.current = null;
      setSelectedSummary(null);
      return;
    }

    if (!/^\d{4,5}$/.test(cleanNumber)) {
      setError('Please enter a valid 5-digit train number (e.g. 11013).');
      setTrainData(null);
      setActiveTrainNumber(null);
      activeTrainRef.current = null;
      setSelectedSummary(null);
      return;
    }

    // Set selected summary immediately for instant UI feedback
    if (summaryObj) {
      setSelectedSummary(summaryObj);
    } else {
      const match = summaryData.trains.find((t) => String(t.train_number) === cleanNumber);
      if (match) setSelectedSummary(match);
    }

    const reqId = ++currentRequestIdRef.current;
    activeTrainRef.current = cleanNumber;
    setActiveTrainNumber(cleanNumber);
    setTrainNumber(cleanNumber);
    setError(null);
    setRefreshError(null);
    setLoading(true);

    try {
      const data = await getTrain(cleanNumber);

      if (reqId === currentRequestIdRef.current) {
        setTrainData(data);
        setSelectedSummary(null);
        setLastUpdated(new Date());
        setTimeAgo('Just now');
      }
    } catch (err) {
      if (reqId === currentRequestIdRef.current) {
        setTrainData(null);

        if (!err.response) {
          setError(
            'Unable to connect to backend server. If using Render free tier, the backend may take up to a minute to wake up.'
          );
        } else {
          const status = err.response.status;
          const upstreamMsg = err.response.data?.message;

          if (status === 404) {
            setError(upstreamMsg || `Train '${cleanNumber}' could not be found or is not currently active.`);
          } else if (status === 401) {
            setError('Unauthorized: Railway API access issue. Please verify backend configuration.');
          } else if (status === 502 || status === 503 || status === 504) {
            setError('Live railway service is temporarily unavailable. Please try again later.');
          } else if (status === 400) {
            setError(upstreamMsg || 'Unable to process train tracking request.');
          } else {
            setError(upstreamMsg || 'An unexpected error occurred while fetching train information.');
          }
        }
      }
    } finally {
      if (reqId === currentRequestIdRef.current) {
        setLoading(false);
      }
    }
  };

  const handleTrainSelect = (num, trainObj) => {
    executeSearch(num, trainObj);
    if (mapSectionRef.current) {
      mapSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  };

  const handleInspectDetails = () => {
    setDeepDetailsExpanded(true);
    if (deepDetailsRef.current) {
      deepDetailsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleCenterMap = () => {
    if (mapSectionRef.current) {
      mapSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* 1. Global Live Status Bar */}
      <LiveIndicator
        lastUpdated={lastUpdated}
        timeAgo={timeAgo}
        isRefreshing={isRefreshing}
        refreshError={refreshError}
        onRefresh={refreshTrainData}
        telemetrySource={trainData?.telemetry_source || 'live_railradar'}
      />

      {/* 2. Hero Search Area */}
      <TrainSearch
        inputRef={searchInputRef}
        trainNumber={trainNumber}
        setTrainNumber={(val) => {
          setTrainNumber(val);
          if (error) setError(null);
        }}
        onSearch={executeSearch}
        loading={loading}
      />

      {/* 3. Dynamic KPI Cards (Active, On Time, Delayed, Cancelled) */}
      <KpiCards
        stats={summaryData.stats}
        activeFilter={tableFilter}
        onSelectFilter={(filterId) => {
          setTableFilter(filterId);
          if (tableSectionRef.current) {
            tableSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }}
        loading={summaryLoading}
      />

      {/* Loading Banner for Train Search */}
      {loading && (
        <div className="rounded-2xl border border-blue-200 dark:border-blue-800 bg-white dark:bg-slate-900 p-6 sm:p-8 shadow-xs flex flex-col items-center justify-center text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-950/80 flex items-center justify-center text-blue-600 dark:text-blue-400">
            <Loader2 className="w-6 h-6 animate-spin" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Fetching live telemetry for train #{activeTrainNumber}...
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Calculating station checkpoints, gradient-boosted ML delay forecasts, and corridor geometry
            </p>
          </div>
        </div>
      )}

      {/* Error State Banner */}
      {error && !loading && (
        <div className="rounded-2xl border border-rose-200 dark:border-rose-900 bg-rose-50/80 dark:bg-rose-950/40 p-5 shadow-xs flex items-start space-x-3.5">
          <div className="w-9 h-9 rounded-xl bg-rose-100 dark:bg-rose-900/60 text-rose-600 dark:text-rose-400 flex items-center justify-center shrink-0 mt-0.5">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-bold text-rose-900 dark:text-rose-200">
              Unable to Track Train
            </h4>
            <p className="text-xs text-rose-700 dark:text-rose-300 mt-1 leading-relaxed">
              {error}
            </p>
            <div className="mt-3">
              <button
                type="button"
                onClick={() => executeSearch('11013')}
                className="px-3 py-1 rounded-lg text-xs font-semibold bg-rose-200/80 dark:bg-rose-900/80 text-rose-900 dark:text-rose-200 hover:bg-rose-300 transition cursor-pointer"
              >
                Try sample train 11013 →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 4. MAIN MAP + SELECTED TRAIN AREA (60/40 Layout) */}
      <section ref={mapSectionRef} className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <MapPin className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <h2 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              {trainData ? `Corridor: ${trainData.train?.train_name}` : 'National Corridor Telemetry'}
            </h2>
          </div>
          {trainData && (
            <span className="text-xs font-medium text-slate-500 dark:text-slate-400">
              {trainData.route?.stations?.length || 0} Scheduled Checkpoints
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch min-h-[440px]">
          {/* LEFT: 60% LIVE MAP */}
          <div className="lg:col-span-7 xl:col-span-8 flex flex-col min-h-[380px] sm:min-h-[440px]">
            <TrainMap
              trainData={trainData}
              activeTrains={summaryData.trains}
              onSelectTrain={handleTrainSelect}
              loading={loading}
            />
          </div>

          {/* RIGHT: 40% SELECTED TRAIN PANEL */}
          <div className="lg:col-span-5 xl:col-span-4 flex flex-col">
            <SelectedTrainPanel
              trainData={trainData}
              selectedSummary={selectedSummary}
              loading={loading}
              onInspectDetails={handleInspectDetails}
              onCenterMap={handleCenterMap}
            />
          </div>
        </div>
      </section>

      {/* 5. LIVE ALERTS & NOTICES */}
      <section ref={alertsSectionRef}>
        <AlertsCard
          alerts={summaryData.alerts}
          onSelectTrain={(num) => handleTrainSelect(num)}
        />
      </section>

      {/* 6. TRAIN LIST / TABLE REDESIGN */}
      <section ref={tableSectionRef}>
        <TrainTable
          trains={summaryData.trains}
          selectedTrainNumber={activeTrainNumber}
          onSelectTrain={handleTrainSelect}
          loading={summaryLoading}
          activeFilter={tableFilter}
          onFilterChange={setTableFilter}
        />
      </section>

      {/* 7. DEEP-DIVE INTELLIGENCE SECTION (When a train is selected) */}
      {trainData && !loading && (
        <section
          ref={deepDetailsRef}
          className="pt-6 border-t border-slate-200/90 dark:border-slate-800 space-y-6"
        >
          {/* Section Header with Collapse Toggle */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-xl bg-blue-600 text-white flex items-center justify-center">
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                  Train Intelligence &amp; ML Arrival Predictions
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Detailed timetable variance, upcoming stop forecasts, and station progression
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setDeepDetailsExpanded(!deepDetailsExpanded)}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 shadow-2xs hover:bg-slate-50 transition cursor-pointer"
            >
              <span>{deepDetailsExpanded ? 'Collapse' : 'Expand Details'}</span>
              {deepDetailsExpanded ? (
                <ChevronUp className="w-3.5 h-3.5" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" />
              )}
            </button>
          </div>

          {deepDetailsExpanded && (
            <div className="space-y-6 animate-in fade-in-50 duration-200">
              {/* Train Overview Banner */}
              <TrainOverview trainData={trainData} />

              {/* Status & ML Forecast Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                <CurrentStatusCard liveStatus={trainData.live_status} />
                <PredictionCard
                  prediction={trainData.prediction}
                  liveDelayMinutes={trainData.live_status?.current_delay_minutes}
                />
              </div>

              {/* Delay Distinction Comparison Banner */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 p-4 sm:p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center space-x-3 min-w-0">
                  <div className="w-2.5 h-10 rounded-full bg-gradient-to-b from-blue-600 to-indigo-600 hidden sm:block shrink-0" />
                  <div className="min-w-0">
                    <div className="text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                      Ground Telemetry vs Machine Learning Forecast
                    </div>
                    <div className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 font-medium mt-0.5">
                      Ground reality reflects the current recorded delay. ML forecast models dynamic corridor recovery and traffic congestion.
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-3 shrink-0">
                  {/* Live delay */}
                  <div className="px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700 text-center min-w-[110px]">
                    <div className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                      LIVE DELAY
                    </div>
                    <div className="text-base font-bold font-mono text-slate-900 dark:text-white mt-0.5">
                      {formatDelayDisplay(trainData.live_status?.current_delay_minutes)}
                    </div>
                  </div>

                  <span className="text-slate-400 font-bold text-xs hidden sm:inline">vs</span>

                  {/* ML delay */}
                  <div className="px-3 py-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 text-center min-w-[110px]">
                    <div className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">
                      ML PREDICTED
                    </div>
                    <div className="text-base font-bold font-mono text-indigo-700 dark:text-indigo-300 mt-0.5">
                      {formatDelayDisplay(trainData.prediction?.predicted_delay_minutes)}
                    </div>
                  </div>
                </div>
              </div>

              {/* ETA Delay Progression Chart */}
              <ETADelayChart trainData={trainData} />

              {/* Next Station & Destination Cards */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                <NextStationCard prediction={trainData.prediction} />
                <DestinationCard
                  train={trainData.train}
                  prediction={trainData.prediction}
                  route={trainData.route}
                />
              </div>

              {/* Station Progression Route Timeline */}
              <RouteTimeline trainData={trainData} />
            </div>
          )}
        </section>
      )}
    </div>
  );
};

export default Home;
