/**
 * Workflow result display with download links and WordPress publishing.
 */

import React, { useState } from 'react';
import { useWizardStore } from '../../store/wizardStore';
import { getDownloadUrl } from '../../api/workflow';
import { publishToWordPress } from '../../api/publish';
import { WordPressPublishResponse } from '../../api/types';

function extractTitle(preview?: string): string {
  if (!preview) return '';
  // Try to grab a markdown heading
  const headingMatch = preview.match(/^#{1,3}\s+(.+)/m);
  if (headingMatch) return headingMatch[1].trim();
  // Fall back to first non-empty line
  const firstLine = preview.split('\n').find((l) => l.trim());
  return firstLine ? firstLine.trim().slice(0, 120) : '';
}

export const WorkflowResult: React.FC = () => {
  const { jobResult, jobId, resetWizard } = useWizardStore();

  const [publishOpen, setPublishOpen] = useState(false);
  const [title, setTitle] = useState(() => extractTitle(jobResult?.content_full ?? jobResult?.content_preview ?? ''));
  const [content, setContent] = useState(jobResult?.content_full ?? jobResult?.content_preview ?? '');
  const [status, setStatus] = useState<'draft' | 'publish'>('draft');
  const [categories, setCategories] = useState('');
  const [tags, setTags] = useState('');
  const [wpUrl, setWpUrl] = useState('');
  const [wpUser, setWpUser] = useState('');
  const [wpPass, setWpPass] = useState('');
  const [publishing, setPublishing] = useState(false);
  const [publishResult, setPublishResult] = useState<WordPressPublishResponse | null>(null);
  const [publishError, setPublishError] = useState<string | null>(null);

  if (!jobResult || !jobId) return null;

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const splitCommas = (s: string) =>
    s.split(',').map((t) => t.trim()).filter(Boolean);

  const handlePublish = async () => {
    setPublishing(true);
    setPublishError(null);
    setPublishResult(null);
    try {
      const result = await publishToWordPress({
        title,
        content,
        content_format: 'markdown',
        status,
        category_names: splitCommas(categories),
        tag_names: splitCommas(tags),
        credentials:
          wpUrl || wpUser || wpPass
            ? { wp_url: wpUrl || undefined, username: wpUser || undefined, app_password: wpPass || undefined }
            : undefined,
      });
      setPublishResult(result);
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        (err instanceof Error ? err.message : 'Publish failed');
      setPublishError(msg);
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Success header */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
          <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-800">Content Generated!</h2>
        <p className="text-gray-600 mt-2">Your content has been successfully created.</p>
      </div>

      {/* Content preview */}
      {jobResult.content_preview && (
        <div className="border rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-2 border-b">
            <h4 className="font-medium text-gray-700">Content Preview</h4>
          </div>
          <div className="p-4 max-h-48 overflow-y-auto">
            <p className="text-gray-700 whitespace-pre-wrap text-sm">{jobResult.content_preview}</p>
          </div>
        </div>
      )}

      {/* Download files */}
      {jobResult.outputs.length > 0 && (
        <div className="border rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-2 border-b">
            <h4 className="font-medium text-gray-700">Generated Files</h4>
          </div>
          <div className="p-4 space-y-3">
            {jobResult.outputs.map((file) => (
              <div key={file.file_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <span className="text-primary-600 font-bold text-xs">{file.format.toUpperCase()}</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">{file.filename}</p>
                    <p className="text-sm text-gray-500">{formatBytes(file.size_bytes)}</p>
                  </div>
                </div>
                <a href={getDownloadUrl(jobId, file.file_id)} download={file.filename} className="btn-primary text-sm">
                  Download
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Publish to WordPress */}
      <div className="border rounded-lg overflow-hidden">
        <button
          type="button"
          onClick={() => setPublishOpen((o) => !o)}
          className="w-full flex items-center justify-between bg-gray-50 px-4 py-3 hover:bg-gray-100 transition-colors"
        >
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
            </svg>
            <span className="font-medium text-gray-700">Publish to WordPress</span>
          </div>
          <svg
            className={`w-4 h-4 text-gray-500 transition-transform ${publishOpen ? 'rotate-180' : ''}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {publishOpen && (
          <div className="p-4 space-y-4">
            {publishResult ? (
              <div className="rounded-lg bg-green-50 border border-green-200 p-4 space-y-2">
                <p className="font-semibold text-green-800">Published successfully!</p>
                <p className="text-sm text-green-700">
                  Status: <span className="font-medium">{publishResult.status}</span>
                </p>
                <div className="flex gap-3 text-sm">
                  <a href={publishResult.post_url} target="_blank" rel="noopener noreferrer"
                    className="text-blue-600 hover:underline">View post</a>
                  <a href={publishResult.edit_url} target="_blank" rel="noopener noreferrer"
                    className="text-blue-600 hover:underline">Edit in WordPress</a>
                </div>
                <button type="button" onClick={() => setPublishResult(null)}
                  className="text-xs text-gray-500 hover:text-gray-700 underline">
                  Publish again
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {publishError && (
                  <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                    {publishError}
                  </div>
                )}

                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Post title</label>
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter post title"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Content
                    </label>
                    <textarea
                      value={content}
                      onChange={(e) => setContent(e.target.value)}
                      rows={6}
                      className="w-full border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Paste your content here (Markdown accepted)"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                      <select
                        value={status}
                        onChange={(e) => setStatus(e.target.value as 'draft' | 'publish')}
                        className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="draft">Draft</option>
                        <option value="publish">Publish immediately</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Categories <span className="font-normal text-gray-500">(comma-separated)</span>
                      </label>
                      <input
                        type="text"
                        value={categories}
                        onChange={(e) => setCategories(e.target.value)}
                        className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Tech, Marketing"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tags <span className="font-normal text-gray-500">(comma-separated)</span>
                    </label>
                    <input
                      type="text"
                      value={tags}
                      onChange={(e) => setTags(e.target.value)}
                      className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="AI, content marketing"
                    />
                  </div>

                  {/* Optional credential override */}
                  <details className="text-sm">
                    <summary className="cursor-pointer text-gray-500 hover:text-gray-700">
                      WordPress credentials (leave blank to use server env vars)
                    </summary>
                    <div className="mt-2 space-y-2 pl-2 border-l-2 border-gray-200">
                      <input
                        type="url"
                        value={wpUrl}
                        onChange={(e) => setWpUrl(e.target.value)}
                        className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="https://yoursite.com"
                      />
                      <input
                        type="text"
                        value={wpUser}
                        onChange={(e) => setWpUser(e.target.value)}
                        className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Username"
                      />
                      <input
                        type="password"
                        value={wpPass}
                        onChange={(e) => setWpPass(e.target.value)}
                        className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Application password"
                      />
                    </div>
                  </details>
                </div>

                <button
                  type="button"
                  onClick={handlePublish}
                  disabled={publishing || !title.trim() || !content.trim()}
                  className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {publishing ? 'Publishing…' : status === 'publish' ? 'Publish to WordPress' : 'Save as Draft'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Workflow details */}
      <div className="border rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-4 py-2 border-b">
          <h4 className="font-medium text-gray-700">Details</h4>
        </div>
        <div className="p-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Workflow Type</span>
            <span className="text-gray-800">{jobResult.workflow_type}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Job ID</span>
            <span className="text-gray-800 font-mono text-xs">{jobId}</span>
          </div>
          {jobResult.start_time && (
            <div className="flex justify-between">
              <span className="text-gray-500">Started</span>
              <span className="text-gray-800">{new Date(jobResult.start_time).toLocaleString()}</span>
            </div>
          )}
          {jobResult.end_time && (
            <div className="flex justify-between">
              <span className="text-gray-500">Completed</span>
              <span className="text-gray-800">{new Date(jobResult.end_time).toLocaleString()}</span>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-center gap-4">
        <button type="button" onClick={resetWizard} className="btn-primary">
          Create More Content
        </button>
      </div>
    </div>
  );
};
