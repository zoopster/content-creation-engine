/**
 * Workflow progress display during execution.
 */

import React from 'react';
import { useWizardStore } from '../../store/wizardStore';
import { JobStatus } from '../../api/types';

export const WorkflowProgress: React.FC = () => {
  const { jobStatus, executionError } = useWizardStore();

  if (!jobStatus) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Starting workflow...</p>
      </div>
    );
  }

  const isRunning = jobStatus.status === JobStatus.RUNNING;
  const isPending = jobStatus.status === JobStatus.PENDING;
  const isFailed = jobStatus.status === JobStatus.FAILED;

  return (
    <div className="space-y-6">
      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-600">
            {jobStatus.current_step || 'Processing...'}
          </span>
          <span className="text-gray-600">{Math.round(jobStatus.progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${
              isFailed ? 'bg-red-500' : 'bg-primary-600'
            }`}
            style={{ width: `${jobStatus.progress}%` }}
          />
        </div>
      </div>

      {/* Status indicator */}
      <div className="flex items-center justify-center gap-3">
        {(isRunning || isPending) && (
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
        )}
        <span
          className={`font-medium ${
            isFailed ? 'text-red-600' : 'text-primary-600'
          }`}
        >
          {isPending && 'Queued...'}
          {isRunning && 'Processing...'}
          {isFailed && 'Failed'}
        </span>
      </div>

      {/* Steps completed */}
      {jobStatus.steps_completed.length > 0 && (
        <div className="border rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-2 border-b">
            <h4 className="font-medium text-gray-700">Steps Completed</h4>
          </div>
          <div className="p-4 space-y-2">
            {jobStatus.steps_completed.map((step, index) => (
              <div
                key={index}
                className="flex items-center gap-2 text-sm"
              >
                {step.status === 'completed' ? (
                  <span className="text-green-500">✓</span>
                ) : step.status === 'failed' ? (
                  <span className="text-red-500">✗</span>
                ) : (
                  <span className="text-gray-400">○</span>
                )}
                <span className="text-gray-700">
                  {step.step.replace(/_/g, ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error message */}
      {(executionError || jobStatus.error_message) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="font-medium text-red-800 mb-2">Error</h4>
          <p className="text-red-700 text-sm">
            {executionError || jobStatus.error_message}
          </p>
        </div>
      )}
    </div>
  );
};
