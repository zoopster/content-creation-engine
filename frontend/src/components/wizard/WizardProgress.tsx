/**
 * Wizard progress indicator showing step progression.
 */

import React from 'react';

interface WizardProgressProps {
  steps: string[];
  currentStep: number;
}

export const WizardProgress: React.FC<WizardProgressProps> = ({
  steps,
  currentStep,
}) => {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <React.Fragment key={step}>
            {/* Step indicator */}
            <div className="flex flex-col items-center">
              <div
                className={`
                  w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-colors
                  ${
                    index < currentStep
                      ? 'bg-primary-600 text-white'
                      : index === currentStep
                        ? 'bg-primary-600 text-white ring-4 ring-primary-200'
                        : 'bg-gray-200 text-gray-500'
                  }
                `}
              >
                {index < currentStep ? (
                  <svg
                    className="w-5 h-5"
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
                ) : (
                  index + 1
                )}
              </div>
              <span
                className={`
                  mt-2 text-xs font-medium text-center max-w-[80px]
                  ${index <= currentStep ? 'text-primary-600' : 'text-gray-400'}
                `}
              >
                {step}
              </span>
            </div>

            {/* Connector line */}
            {index < steps.length - 1 && (
              <div
                className={`
                  flex-1 h-1 mx-2 rounded transition-colors
                  ${index < currentStep ? 'bg-primary-600' : 'bg-gray-200'}
                `}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
