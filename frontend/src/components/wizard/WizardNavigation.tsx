/**
 * Wizard navigation buttons.
 */

import React from 'react';

interface WizardNavigationProps {
  isFirstStep: boolean;
  isLastStep: boolean;
  onNext: () => void;
  onPrev: () => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
  canProceed?: boolean;
}

export const WizardNavigation: React.FC<WizardNavigationProps> = ({
  isFirstStep,
  isLastStep,
  onNext,
  onPrev,
  onSubmit,
  isSubmitting = false,
  canProceed = true,
}) => {
  return (
    <div className="flex justify-between mt-8">
      <button
        type="button"
        onClick={onPrev}
        disabled={isFirstStep}
        className="btn-secondary"
      >
        Back
      </button>

      {isLastStep ? (
        <button
          type="button"
          onClick={onSubmit}
          disabled={isSubmitting || !canProceed}
          className="btn-primary"
        >
          {isSubmitting ? (
            <span className="flex items-center gap-2">
              <svg
                className="animate-spin h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Submitting...
            </span>
          ) : (
            'Submit'
          )}
        </button>
      ) : (
        <button
          type="button"
          onClick={onNext}
          disabled={!canProceed}
          className="btn-primary"
        >
          Next
        </button>
      )}
    </div>
  );
};
