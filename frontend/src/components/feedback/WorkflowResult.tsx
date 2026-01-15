/**
 * Workflow result display with download links.
 */

import React from 'react';
import { useWizardStore } from '../../store/wizardStore';
import { getDownloadUrl } from '../../api/workflow';

export const WorkflowResult: React.FC = () => {
  const { jobResult, jobId, resetWizard } = useWizardStore();

  if (!jobResult || !jobId) {
    return null;
  }

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Success header */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
          <svg
            className="w-8 h-8 text-green-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-800">Content Generated!</h2>
        <p className="text-gray-600 mt-2">
          Your content has been successfully created.
        </p>
      </div>

      {/* Content preview */}
      {jobResult.content_preview && (
        <div className="border rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-2 border-b">
            <h4 className="font-medium text-gray-700">Content Preview</h4>
          </div>
          <div className="p-4 max-h-48 overflow-y-auto">
            <p className="text-gray-700 whitespace-pre-wrap text-sm">
              {jobResult.content_preview}
            </p>
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
              <div
                key={file.file_id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <span className="text-primary-600 font-bold text-xs">
                      {file.format.toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">{file.filename}</p>
                    <p className="text-sm text-gray-500">
                      {formatBytes(file.size_bytes)}
                    </p>
                  </div>
                </div>
                <a
                  href={getDownloadUrl(jobId, file.file_id)}
                  download={file.filename}
                  className="btn-primary text-sm"
                >
                  Download
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

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
              <span className="text-gray-800">
                {new Date(jobResult.start_time).toLocaleString()}
              </span>
            </div>
          )}
          {jobResult.end_time && (
            <div className="flex justify-between">
              <span className="text-gray-500">Completed</span>
              <span className="text-gray-800">
                {new Date(jobResult.end_time).toLocaleString()}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-center gap-4">
        <button
          type="button"
          onClick={resetWizard}
          className="btn-primary"
        >
          Create More Content
        </button>
      </div>
    </div>
  );
};
