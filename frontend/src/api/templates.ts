/**
 * Templates and metadata API calls.
 */

import { apiClient } from './client';
import {
  BrandTemplateListResponse,
  ContentTypeListResponse,
  PlatformListResponse,
} from './types';

export const getTemplates = async (): Promise<BrandTemplateListResponse> => {
  const response = await apiClient.get<BrandTemplateListResponse>('/api/templates');
  return response.data;
};

export const getContentTypes = async (): Promise<ContentTypeListResponse> => {
  const response = await apiClient.get<ContentTypeListResponse>('/api/content-types');
  return response.data;
};

export const getPlatforms = async (): Promise<PlatformListResponse> => {
  const response = await apiClient.get<PlatformListResponse>('/api/platforms');
  return response.data;
};
