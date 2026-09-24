import { useState, useCallback } from 'react';
import { getTrain } from '../services/api';

/**
 * Custom hook for managing train search, tracking state, and ETA predictions.
 * Ready for future integration in Chunk 12+.
 */
export const useTrain = () => {
  const [trainData, setTrainData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTrain = useCallback(async (trainNumber) => {
    if (!trainNumber) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getTrain(trainNumber);
      setTrainData(data);
      return data;
    } catch (err) {
      const message = err.response?.data?.message || err.message || 'Failed to fetch train tracking details';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setTrainData(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    trainData,
    loading,
    error,
    fetchTrain,
    reset,
  };
};

export default useTrain;
