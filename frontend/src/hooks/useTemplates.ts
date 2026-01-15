/**
 * Hook for fetching brand templates.
 */

import { useState, useEffect } from 'react';
import { BrandTemplate } from '../api/types';
import { getTemplates } from '../api/templates';

interface UseTemplatesReturn {
  templates: BrandTemplate[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useTemplates = (): UseTemplatesReturn => {
  const [templates, setTemplates] = useState<BrandTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplates = async () => {
    setIsLoading(true);
    try {
      const response = await getTemplates();
      setTemplates(response.templates);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load templates');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  return { templates, isLoading, error, refetch: fetchTemplates };
};
