import { useState, useEffect } from 'react';
import { getEarningsData } from '../services/geminiService';
import type { EarningsCalendarData } from '../types';

export const useEarningsData = () => {
  const [data, setData] = useState<EarningsCalendarData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getEarningsData();
      setData(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An unknown error occurred.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
};