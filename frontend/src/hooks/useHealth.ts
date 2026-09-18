import { useState, useEffect, useCallback } from 'react';
import { fetchHealthStatus } from '../services/api';
import type { HealthResponse } from '../types';

export function useHealth() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const check = useCallback(async () => {
    try {
      const data = await fetchHealthStatus();
      setHealth(data);
      setError(null);
    } catch (err) {
      setError('Backend unreachable');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    check();
    // Refresh every 30 seconds
    const id = setInterval(check, 30_000);
    return () => clearInterval(id);
  }, [check]);

  return { health, loading, error, refetch: check };
}
