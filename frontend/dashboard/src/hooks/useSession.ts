import { useState, useEffect } from 'react';
import * as api from '../services/api';

export function useSession() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const createSession = async () => {
      try {
        setLoading(true);
        const id = await api.createSession();
        setSessionId(id);
        setError(null);
      } catch (err) {
        setError('创建会话失败: ' + (err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    createSession();
  }, []);

  return { sessionId, loading, error };
}