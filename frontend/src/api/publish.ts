/**
 * WordPress publish API calls.
 */

import { apiClient } from './client';
import { WordPressPublishRequest, WordPressPublishResponse } from './types';

export const publishToWordPress = async (
  request: WordPressPublishRequest
): Promise<WordPressPublishResponse> => {
  const response = await apiClient.post<WordPressPublishResponse>(
    '/api/publish/wordpress',
    request
  );
  return response.data;
};

export const verifyWordPressConnection = async (
  wp_url?: string,
  username?: string,
  app_password?: string
): Promise<{ connected: boolean; site_name?: string; site_url?: string }> => {
  const params = new URLSearchParams();
  if (wp_url) params.set('wp_url', wp_url);
  if (username) params.set('username', username);
  if (app_password) params.set('app_password', app_password);

  const response = await apiClient.get(
    `/api/publish/wordpress/verify?${params.toString()}`
  );
  return response.data;
};
