/**
 * Main wizard container - orchestrates the multi-step form.
 */

import React, { useCallback } from 'react';
import { useWizardStore } from '../../store/wizardStore';
import { useWorkflowStatus } from '../../hooks/useWorkflowStatus';
import { executeWorkflow } from '../../api/workflow';
import { JobStatus } from '../../api/types';

import { WizardProgress } from './WizardProgress';
import { WizardNavigation } from './WizardNavigation';
import { BasicRequestStep } from '../forms/BasicRequestStep';
import { AudienceToneStep } from '../forms/AudienceToneStep';
import { SocialSettingsStep } from '../forms/SocialSettingsStep';
import { BrandTemplateStep } from '../forms/BrandTemplateStep';
import { OutputSettingsStep } from '../forms/OutputSettingsStep';
import { ReviewSubmitStep } from '../forms/ReviewSubmitStep';
import { WorkflowProgress as WorkflowProgressDisplay } from '../feedback/WorkflowProgress';
import { WorkflowResult } from '../feedback/WorkflowResult';

export const WizardContainer: React.FC = () => {
  const {
    currentStep,
    formData,
    shouldShowSocialStep,
    getTotalSteps,
    nextStep,
    prevStep,
    isSubmitting,
    setSubmitting,
    setJobId,
    setExecutionError,
    jobStatus,
    jobResult,
    isStepValid,
    resetExecution,
  } = useWizardStore();

  const { startPolling } = useWorkflowStatus();

  const showSocialStep = shouldShowSocialStep();

  // Build step list dynamically based on content type selection
  const steps = [
    { id: 'basic', title: 'Content Request', component: BasicRequestStep },
    { id: 'audience', title: 'Audience & Tone', component: AudienceToneStep },
    ...(showSocialStep
      ? [{ id: 'social', title: 'Platform Settings', component: SocialSettingsStep }]
      : []),
    { id: 'brand', title: 'Brand Template', component: BrandTemplateStep },
    { id: 'output', title: 'Output Settings', component: OutputSettingsStep },
    { id: 'review', title: 'Review & Submit', component: ReviewSubmitStep },
  ];

  const CurrentStepComponent = steps[currentStep]?.component;
  const isLastStep = currentStep === steps.length - 1;
  const isFirstStep = currentStep === 0;

  const handleSubmit = useCallback(async () => {
    setSubmitting(true);
    setExecutionError(null);

    try {
      const response = await executeWorkflow(formData);
      setJobId(response.job_id);
      startPolling(response.job_id);
    } catch (error) {
      setExecutionError(
        error instanceof Error ? error.message : 'Failed to start workflow'
      );
      setSubmitting(false);
    }
  }, [formData, setSubmitting, setJobId, setExecutionError, startPolling]);

  // Show result view if workflow completed successfully
  if (jobResult && jobResult.success) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="card">
          <WorkflowResult />
        </div>
      </div>
    );
  }

  // Show progress view if workflow is running
  if (isSubmitting || (jobStatus && jobStatus.status !== JobStatus.FAILED)) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
            Generating Content
          </h2>
          <WorkflowProgressDisplay />
          {jobStatus?.status === JobStatus.FAILED && (
            <div className="mt-6 text-center">
              <button
                type="button"
                onClick={resetExecution}
                className="btn-secondary"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <WizardProgress steps={steps.map((s) => s.title)} currentStep={currentStep} />

      <div className="card mt-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">
          {steps[currentStep]?.title}
        </h2>

        {CurrentStepComponent && <CurrentStepComponent />}

        <WizardNavigation
          isFirstStep={isFirstStep}
          isLastStep={isLastStep}
          onNext={nextStep}
          onPrev={prevStep}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          canProceed={isStepValid(currentStep)}
        />
      </div>
    </div>
  );
};
