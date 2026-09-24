import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Loader2, AlertCircle, Train, ShieldCheck, Compass, Sparkles, RefreshCw, Radio, AlertTriangle } from 'lucide-react';
import { getTrain } from '../services/api';
import TrainSearch from '../components/TrainSearch';
import TrainOverview from '../components/TrainOverview';
import CurrentStatusCard from '../components/CurrentStatusCard';
import PredictionCard from '../components/PredictionCard';
import NextStationCard from '../components/NextStationCard';
import DestinationCard from '../components/DestinationCard';
import ETADelayChart from '../components/ETADelayChart';
import TrainMap from '../components/TrainMap';
import RouteTimeline from '../components/RouteTimeline';
import { formatDelayDisplay } from '../utils/formatters';

const REFRESH_INTERVAL_MS = 30000; // 30 seconds automatic polling interval

export const Home = () => {
  const [trainNumber, setTrainNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [trainData, setTrainData] = useState(null);

  // Live Auto-Refresh State
  const [activeTrainNumber, setActiveTrainNumber] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [timeAgo, setTimeAgo] = useState('Just now');

  // Refs for tracking active lifecycle, preventing overlapping/stale calls
  const currentRequestIdRef = useRef(0);
  const pollingTimerRef = useRef(null);
  const activeTrainRef = useRef(null);
  const isRefreshingRef = useRef(false);

  // Update relative elapsed time every 5 seconds via timer callback
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

  // Background refresh function
  const refreshTrainData = useCallback(async () => {
    const targetTrain = activeTrainRef.current;
    if (!targetTrain || isRefreshingRef.current) return;

    isRefreshingRef.current = true;
    setIsRefreshing(true);
    const reqId = ++currentRequestIdRef.current;

    try {
      const refreshedData = await getTrain(targetTrain);

      // Verify request is still the most recent and train hasn't changed
      if (reqId === currentRequestIdRef.current && activeTrainRef.current === targetTrain) {
        setTrainData(refreshedData);
        setLastUpdated(new Date());
        setTimeAgo('Just now');
        setRefreshError(null);
      }
    } catch (err) {
      // Gracefully handle refresh failure without clearing existing train data
      if (reqId === currentRequestIdRef.current) {
        console.warn(`[AutoRefresh] Background update failed for train ${targetTrain}:`, err.message);
        setRefreshError('Temporary live telemetry update hiccup. Retrying in 30s...');
      }
    } finally {
      if (reqId === currentRequestIdRef.current) {
        isRefreshingRef.current = false;
        setIsRefreshing(false);
      }
    }
  }, []);

  // Set up and clean up automatic polling interval whenever active train changes
  useEffect(() => {
    // Clear any existing polling timer
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current);
      pollingTimerRef.current = null;
    }

    if (!activeTrainNumber) {
      return;
    }

    // Initialize recurring 30s interval
    pollingTimerRef.current = setInterval(() => {
      refreshTrainData();
    }, REFRESH_INTERVAL_MS);

    // Cleanup on train change or unmount
    return () => {
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
        pollingTimerRef.current = null;
      }
    };
  }, [activeTrainNumber, refreshTrainData]);

  // Explicit manual search execution
  const executeSearch = async (numToSearch) => {
    const cleanNumber = String(numToSearch || '').trim();

    // 1. Validation
    if (!cleanNumber) {
      setError('Please enter a train number.');
      setTrainData(null);
      setActiveTrainNumber(null);
      activeTrainRef.current = null;
      return;
    }

    if (!/^\d{4,5}$/.test(cleanNumber)) {
      setError('Please enter a valid 5-digit train number (e.g. 11013).');
      setTrainData(null);
      setActiveTrainNumber(null);
      activeTrainRef.current = null;
      return;
    }

    // 2. Clear previous polling, errors, and in-flight requests
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current);
      pollingTimerRef.current = null;
    }

    const reqId = ++currentRequestIdRef.current;
    activeTrainRef.current = cleanNumber;
    setError(null);
    setRefreshError(null);
    setLoading(true);

    // 3. API execution
    try {
      const data = await getTrain(cleanNumber);

      if (reqId === currentRequestIdRef.current) {
        setTrainData(data);
        setActiveTrainNumber(cleanNumber);
        setLastUpdated(new Date());
        setTimeAgo('Just now');
      }
    } catch (err) {
      if (reqId === currentRequestIdRef.current) {
        setTrainData(null);
        setActiveTrainNumber(null);
        activeTrainRef.current = null;

        // Clean, user-friendly error formatting (never exposing stack traces, keys, or paths)
        if (!err.response) {
          setError('Unable to connect to backend server. If using Render free tier, the backend may take up to a minute to wake up.');
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

  return (
    <div className="space-y-6 pb-6">
      {/* Search Section */}
      <TrainSearch
        trainNumber={trainNumber}
        setTrainNumber={(val) => {
          setTrainNumber(val);
          if (error) setError(null);
        }}
        onSearch={executeSearch}
        loading={loading}
      />

      {/* Loading State Banner */}
      {loading && (
        <div
          id="loading-state"
          className="relative overflow-hidden rounded-[28px] border border-blue-200 bg-gradient-to-br from-white via-blue-50 to-sky-50 p-8 shadow-[0_20px_50px_rgba(59,130,246,0.08)] flex flex-col items-center justify-center text-center space-y-3"
        >
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.12),transparent_35%)]" />
          <div className="relative w-14 h-14 rounded-full bg-blue-100 ring-8 ring-blue-50 flex items-center justify-center text-blue-600 shadow-lg shadow-blue-200/40">
            <Loader2 className="w-7 h-7 animate-spin" />
          </div>
          <div className="relative">
            <h3 className="text-base font-black text-slate-900">Fetching live train information...</h3>
            <p className="text-xs text-slate-500 mt-1.5">
              Querying real-time satellite telemetry and calculating ML delay forecasts
            </p>
          </div>
        </div>
      )}

      {/* Error State Banner */}
      {error && !loading && (
        <div
          id="error-state"
          className="rounded-[24px] border border-red-200 bg-gradient-to-r from-red-50 to-rose-50 p-6 shadow-[0_16px_35px_rgba(239,68,68,0.08)] flex items-start space-x-4"
        >
          <div className="w-11 h-11 rounded-2xl bg-red-100 text-red-600 flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-black text-red-900">Unable to fetch train information</h3>
            <p className="text-xs text-red-700 mt-1.5 leading-relaxed">{error}</p>
          </div>
        </div>
      )}

      {/* Empty State (Before searching) */}
      {!loading && !trainData && !error && (
        <div
          id="empty-state"
          className="relative overflow-hidden rounded-[30px] border border-sky-100 bg-gradient-to-br from-white via-sky-50/80 to-indigo-50 p-8 sm:p-12 shadow-[0_24px_60px_rgba(37,99,235,0.08)] text-center"
        >
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.12),transparent_35%)]" />
          <div className="relative">
            <div className="w-20 h-20 rounded-[24px] bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center mx-auto text-white mb-5 shadow-lg shadow-blue-500/20 ring-8 ring-blue-100/80">
              <Train className="w-9 h-9" />
            </div>
            <h3 className="text-lg sm:text-xl font-black text-slate-800 tracking-tight">
              Search for a train to view live status and predicted ETA.
            </h3>
            <p className="text-xs sm:text-sm text-slate-500 mt-2 max-w-md mx-auto leading-relaxed">
              Enter a 5-digit Indian Railways train number above or pick a sample train to view real-time location, live delays, and machine learning predictions.
            </p>

            {/* Value Props */}
            <div className="mt-8 pt-6 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl mx-auto text-left">
              <div className="flex items-start space-x-3 p-3 rounded-2xl bg-gradient-to-br from-sky-50 to-white border border-sky-100 shadow-sm">
                <div className="w-9 h-9 rounded-xl bg-sky-100 flex items-center justify-center shrink-0">
                  <Compass className="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-900">Live GPS Telemetry</div>
                  <div className="text-[11px] text-slate-500 mt-0.5">Real-time station checkpoints &amp; speed</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-2xl bg-gradient-to-br from-violet-50 to-white border border-violet-100 shadow-sm">
                <div className="w-9 h-9 rounded-xl bg-violet-100 flex items-center justify-center shrink-0">
                  <Sparkles className="w-4 h-4 text-indigo-600" />
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-900">ML Delay Prediction</div>
                  <div className="text-[11px] text-slate-500 mt-0.5">Predicts dynamic recovery &amp; congestion</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-2xl bg-gradient-to-br from-emerald-50 to-white border border-emerald-100 shadow-sm">
                <div className="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center shrink-0">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-900">Dynamic Station ETA</div>
                  <div className="text-[11px] text-slate-500 mt-0.5">Calculated expected arrival for upcoming stops</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Train Dashboard Results (When trainData is present) */}
      {trainData && !loading && (
        <div id="train-dashboard" className="space-y-6">
          {/* Live Telemetry & Auto-Refresh Status Bar */}
          <div
            id="live-refresh-bar"
            className="bg-gradient-to-r from-white via-sky-50/80 to-indigo-50/80 backdrop-blur-sm border border-sky-100 rounded-2xl px-4 py-2.5 shadow-[0_12px_25px_rgba(59,130,246,0.08)] flex flex-wrap items-center justify-between gap-3 text-xs"
          >
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
              <span className="font-semibold text-slate-800 flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5 text-emerald-600" />
                {trainData?.telemetry_source === 'live_railradar' ? 'Live Satellite GPS' : 'Real-Time Schedule Tracking'}
              </span>
              <span className="hidden sm:inline-block text-slate-300">|</span>
              <span className="text-slate-500 hidden sm:inline-block">
                {trainData?.telemetry_source === 'live_railradar' ? 'Connected to RailRadar API' : 'Calculated from Live IST Timetable'}
              </span>
            </div>

            <div className="flex items-center space-x-3 ml-auto">
              {refreshError && (
                <div className="flex items-center space-x-1.5 text-amber-700 bg-amber-50 px-2.5 py-1 rounded-md border border-amber-200">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  <span>{refreshError}</span>
                </div>
              )}

              <div className="flex items-center space-x-2 text-slate-600">
                {isRefreshing ? (
                  <span className="flex items-center space-x-1.5 text-blue-600 font-medium">
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Updating live data...</span>
                  </span>
                ) : (
                  <span className="text-slate-500">
                    Last updated:{' '}
                    <span className="font-semibold text-slate-700 font-mono">
                      {timeAgo || 'Just now'}
                    </span>
                  </span>
                )}
              </div>

              <button
                type="button"
                onClick={refreshTrainData}
                disabled={isRefreshing}
                title="Refresh train data now"
                className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition disabled:opacity-50 cursor-pointer disabled:cursor-not-allowed"
              >
                <RefreshCw
                  className={`w-3 h-3 ${isRefreshing ? 'animate-spin text-blue-600' : ''}`}
                />
                <span className="text-[11px]">Refresh</span>
              </button>
            </div>
          </div>

          {/* 1. Train Overview Banner */}
          <TrainOverview trainData={trainData} />

          {/* 2. Primary Status & ML Forecast Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Live Current Status */}
            <CurrentStatusCard liveStatus={trainData.live_status} />

            {/* ML Prediction */}
            <PredictionCard
              prediction={trainData.prediction}
              liveDelayMinutes={trainData.live_status?.current_delay_minutes}
            />
          </div>

          {/* 3. Delay Distinction Highlight Banner */}
          <div className="bg-gradient-to-r from-sky-50 via-white to-indigo-50 rounded-2xl border border-sky-100 p-4 sm:p-5 shadow-[0_12px_30px_rgba(59,130,246,0.08)] flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center space-x-3 min-w-0">
              <div className="w-2.5 h-10 rounded-full bg-gradient-to-b from-blue-600 to-indigo-600 hidden sm:block shrink-0" />
              <div className="min-w-0">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Delay Analysis &amp; Comparison
                </div>
                <div className="text-sm text-slate-700 font-medium mt-0.5">
                  Distinguishing between live ground delay and machine-learning predicted arrival delay
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3 shrink-0">
              {/* Current live delay pill */}
              <div className="px-3.5 py-2 rounded-lg bg-slate-50 border border-slate-200 text-center flex-1 sm:flex-initial">
                <div className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                  LIVE DELAY
                </div>
                <div className="text-base font-bold font-mono text-slate-900 mt-0.5">
                  {formatDelayDisplay(trainData.live_status?.current_delay_minutes)}
                </div>
              </div>

              {/* Arrow or divider */}
              <span className="text-slate-400 font-bold text-sm hidden sm:inline">vs</span>

              {/* ML predicted delay pill */}
              <div className="px-3.5 py-2 rounded-lg bg-indigo-50 border border-indigo-200 text-center flex-1 sm:flex-initial">
                <div className="text-[11px] font-bold text-indigo-700 uppercase tracking-wider">
                  ML PREDICTED DELAY
                </div>
                <div className="text-base font-bold font-mono text-indigo-700 mt-0.5">
                  {formatDelayDisplay(trainData.prediction?.predicted_delay_minutes)}
                </div>
              </div>
            </div>
          </div>

          {/* 4. ETA & Delay Variance Visualization */}
          <ETADelayChart trainData={trainData} />

          {/* 5. Next Station & Destination Corridor Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Next Station Details */}
            <NextStationCard prediction={trainData.prediction} />

            {/* Destination Details */}
            <DestinationCard
              train={trainData.train}
              prediction={trainData.prediction}
              route={trainData.route}
            />
          </div>

          {/* 6. Live Railway Route Map */}
          <TrainMap trainData={trainData} loading={loading} />

          {/* 7. Route & Station Timeline */}
          <RouteTimeline trainData={trainData} />
        </div>
      )}
    </div>
  );
};

export default Home;
