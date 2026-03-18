/**
 * Hook for polling workflow status.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { WorkflowStatusResponse, JobStatus } from '../api/types';
import { getWorkflowStatus, getWorkflowResult } from '../api/workflow';
import { useWizardStore } from '../store/wizardStore';

interface UseWorkflowStatusReturn {
  isPolling: boolean;
  error: string | null;
  startPolling: (jobId: string) => void;
  stopPolling: () => void;
}

const MAX_CONSECUTIVE_FAILURES = 5;

export const useWorkflowStatus = (
  pollInterval: number = 2000
): UseWorkflowStatusReturn => {
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const jobIdRef = useRef<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const consecutiveFailuresRef = useRef<number>(0);

  const { setJobStatus, setJobResult, setExecutionError } = useWizardStore();

  const fetchStatus = useCallback(async (id: string) => {
    try {
      const response = await getWorkflowStatus(id);
      setJobStatus(response);
      setError(null);
      consecutiveFailuresRef.current = 0;

      // Stop polling if workflow is complete
      if (
        response.status === JobStatus.COMPLETED ||
        response.status === JobStatus.FAILED
      ) {
        setIsPolling(false);
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }

        // Fetch final result
        if (response.status === JobStatus.COMPLETED) {
          try {
            const result = await getWorkflowResult(id);
            setJobResult(result);
          } catch (err) {
            console.error('Failed to fetch result:', err);
          }
        } else if (response.error_message) {
          setExecutionError(response.error_message);
        }
      }
    } catch (err) {
      consecutiveFailuresRef.current += 1;
      const message = err instanceof Error ? err.message : 'Failed to fetch status';
      console.warn(`Poll attempt failed (${consecutiveFailuresRef.current}/${MAX_CONSECUTIVE_FAILURES}):`, message);

      // Only surface the error after multiple consecutive failures
      if (consecutiveFailuresRef.current >= MAX_CONSECUTIVE_FAILURES) {
        setError(message);
        setExecutionError(message);
        setIsPolling(false);
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    }
  }, [setJobStatus, setJobResult, setExecutionError]);

  const startPolling = useCallback(
    (id: string) => {
      jobIdRef.current = id;
      setIsPolling(true);
      setError(null);
      consecutiveFailuresRef.current = 0;

      // Immediate first fetch
      fetchStatus(id);

      // Set up polling interval
      intervalRef.current = setInterval(() => {
        if (jobIdRef.current) {
          fetchStatus(jobIdRef.current);
        }
      }, pollInterval);
    },
    [fetchStatus, pollInterval]
  );

  const stopPolling = useCallback(() => {
    setIsPolling(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return { isPolling, error, startPolling, stopPolling };
};
