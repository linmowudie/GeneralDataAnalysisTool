import { useState } from 'react';

interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: () => Promise<void>;
}

export function useApi<T>(apiCall: () => Promise<T>): UseApiReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiCall();
      setData(result);
    } catch (err) {
      setError((err as Error).message || '发生未知错误');
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, execute };
}