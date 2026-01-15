/**
 * Workflow API calls.
 */

import { apiClient } from './client';
import {
  WorkflowFormData,
  WorkflowStatusResponse,
  WorkflowResultResponse,
} from './types';

// Transform frontend form data to API schema (snake_case)
const transformFormData = (formData: WorkflowFormData) => ({
  request_text: formData.requestText,
  content_types: formData.contentTypes,
  priority: formData.priority,
  deadline: formData.deadline || null,
  target_audience: formData.targetAudience,
  tone: formData.tone,
  word_count_min: formData.wordCountMin || null,
  word_count_max: formData.wordCountMax || null,
  social_settings: formData.socialSettings
    ? {
        platform: formData.socialSettings.platform,
        format_type: formData.socialSettings.formatType,
        include_cta: formData.socialSettings.includeCta,
        emoji_density: formData.socialSettings.emojiDensity,
      }
    : null,
  brand_template: formData.brandTemplate,
  output_format: formData.outputFormat,
  include_metadata: formData.includeMetadata,
  page_numbers: formData.pageNumbers,
});

export const executeWorkflow = async (
  formData: WorkflowFormData
): Promise<WorkflowStatusResponse> => {
  const payload = transformFormData(formData);
  const response = await apiClient.post<WorkflowStatusResponse>(
    '/api/workflow/execute',
    payload
  );
  return response.data;
};

export const getWorkflowStatus = async (
  jobId: string
): Promise<WorkflowStatusResponse> => {
  const response = await apiClient.get<WorkflowStatusResponse>(
    `/api/workflow/status/${jobId}`
  );
  return response.data;
};

export const getWorkflowResult = async (
  jobId: string
): Promise<WorkflowResultResponse> => {
  const response = await apiClient.get<WorkflowResultResponse>(
    `/api/workflow/result/${jobId}`
  );
  return response.data;
};

export const getDownloadUrl = (jobId: string, fileId: string): string => {
  const baseUrl = apiClient.defaults.baseURL || '';
  return `${baseUrl}/api/workflow/download/${jobId}/${fileId}`;
};
