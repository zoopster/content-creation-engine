/**
 * Zustand store for wizard form state management.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  WorkflowFormData,
  ContentType,
  ToneType,
  Priority,
  OutputFormat,
  Platform,
  JobStatus,
  WorkflowStatusResponse,
  WorkflowResultResponse,
} from '../api/types';

// Content type defaults for intelligent form population
const CONTENT_TYPE_DEFAULTS: Record<ContentType, Partial<WorkflowFormData>> = {
  [ContentType.ARTICLE]: {
    tone: ToneType.PROFESSIONAL,
    wordCountMin: 800,
    wordCountMax: 1500,
    outputFormat: OutputFormat.HTML,
  },
  [ContentType.BLOG_POST]: {
    tone: ToneType.CONVERSATIONAL,
    wordCountMin: 600,
    wordCountMax: 1200,
    outputFormat: OutputFormat.HTML,
  },
  [ContentType.SOCIAL_POST]: {
    tone: ToneType.CONVERSATIONAL,
    wordCountMin: 50,
    wordCountMax: 280,
    outputFormat: OutputFormat.HTML,
  },
  [ContentType.PRESENTATION]: {
    tone: ToneType.PROFESSIONAL,
    wordCountMin: 500,
    wordCountMax: 1000,
    outputFormat: OutputFormat.PPTX,
  },
  [ContentType.EMAIL]: {
    tone: ToneType.PROFESSIONAL,
    wordCountMin: 100,
    wordCountMax: 500,
    outputFormat: OutputFormat.HTML,
  },
  [ContentType.NEWSLETTER]: {
    tone: ToneType.CONVERSATIONAL,
    wordCountMin: 400,
    wordCountMax: 800,
    outputFormat: OutputFormat.HTML,
  },
  [ContentType.VIDEO_SCRIPT]: {
    tone: ToneType.CONVERSATIONAL,
    wordCountMin: 300,
    wordCountMax: 1000,
    outputFormat: OutputFormat.DOCX,
  },
  [ContentType.WHITEPAPER]: {
    tone: ToneType.TECHNICAL,
    wordCountMin: 2000,
    wordCountMax: 5000,
    outputFormat: OutputFormat.PDF,
  },
  [ContentType.CASE_STUDY]: {
    tone: ToneType.PROFESSIONAL,
    wordCountMin: 800,
    wordCountMax: 1500,
    outputFormat: OutputFormat.PDF,
  },
};

const initialFormData: WorkflowFormData = {
  requestText: '',
  contentTypes: [],
  priority: Priority.NORMAL,
  deadline: undefined,
  targetAudience: 'General audience',
  tone: ToneType.PROFESSIONAL,
  wordCountMin: undefined,
  wordCountMax: undefined,
  socialSettings: undefined,
  brandTemplate: 'professional',
  outputFormat: OutputFormat.HTML,
  includeMetadata: true,
  pageNumbers: true,
};

interface WizardState {
  // Current step (0-indexed)
  currentStep: number;

  // Form data
  formData: WorkflowFormData;

  // Validation state
  validationErrors: Record<string, string>;

  // Workflow execution state
  isSubmitting: boolean;
  jobId: string | null;
  jobStatus: WorkflowStatusResponse | null;
  jobResult: WorkflowResultResponse | null;
  executionError: string | null;

  // Actions
  setCurrentStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;

  updateFormData: (updates: Partial<WorkflowFormData>) => void;
  setFieldError: (field: string, error: string) => void;
  clearFieldError: (field: string) => void;
  clearAllErrors: () => void;

  // Content type change handler (updates defaults)
  handleContentTypesChange: (types: ContentType[]) => void;

  // Workflow execution
  setSubmitting: (isSubmitting: boolean) => void;
  setJobId: (jobId: string | null) => void;
  setJobStatus: (status: WorkflowStatusResponse | null) => void;
  setJobResult: (result: WorkflowResultResponse | null) => void;
  setExecutionError: (error: string | null) => void;

  // Reset
  resetWizard: () => void;
  resetExecution: () => void;

  // Computed
  shouldShowSocialStep: () => boolean;
  getTotalSteps: () => number;
  isStepValid: (step: number) => boolean;
}

export const useWizardStore = create<WizardState>()(
  devtools(
    (set, get) => ({
      currentStep: 0,
      formData: initialFormData,
      validationErrors: {},
      isSubmitting: false,
      jobId: null,
      jobStatus: null,
      jobResult: null,
      executionError: null,

      setCurrentStep: (step) => set({ currentStep: step }),

      nextStep: () => {
        const { currentStep, getTotalSteps, isStepValid } = get();
        if (isStepValid(currentStep) && currentStep < getTotalSteps() - 1) {
          set({ currentStep: currentStep + 1 });
        }
      },

      prevStep: () => {
        const { currentStep } = get();
        if (currentStep > 0) {
          set({ currentStep: currentStep - 1 });
        }
      },

      updateFormData: (updates) => {
        set((state) => ({
          formData: { ...state.formData, ...updates },
        }));
      },

      setFieldError: (field, error) => {
        set((state) => ({
          validationErrors: { ...state.validationErrors, [field]: error },
        }));
      },

      clearFieldError: (field) => {
        set((state) => {
          const newErrors = { ...state.validationErrors };
          delete newErrors[field];
          return { validationErrors: newErrors };
        });
      },

      clearAllErrors: () => {
        set({ validationErrors: {} });
      },

      handleContentTypesChange: (types) => {
        const { formData } = get();

        // Get defaults from primary content type
        const primaryType = types[0];
        const defaults = primaryType ? CONTENT_TYPE_DEFAULTS[primaryType] : {};

        // Initialize social settings if social post selected
        const hasSocialPost = types.includes(ContentType.SOCIAL_POST);
        const socialSettings =
          hasSocialPost && !formData.socialSettings
            ? {
                platform: Platform.LINKEDIN,
                formatType: 'single' as const,
                includeCta: true,
                emojiDensity: 'moderate' as const,
              }
            : hasSocialPost
              ? formData.socialSettings
              : undefined;

        set((state) => ({
          formData: {
            ...state.formData,
            contentTypes: types,
            ...defaults,
            socialSettings,
          },
        }));
      },

      setSubmitting: (isSubmitting) => set({ isSubmitting }),
      setJobId: (jobId) => set({ jobId }),
      setJobStatus: (jobStatus) => set({ jobStatus }),
      setJobResult: (jobResult) => set({ jobResult }),
      setExecutionError: (executionError) => set({ executionError }),

      resetWizard: () => {
        set({
          currentStep: 0,
          formData: initialFormData,
          validationErrors: {},
          isSubmitting: false,
          jobId: null,
          jobStatus: null,
          jobResult: null,
          executionError: null,
        });
      },

      resetExecution: () => {
        set({
          isSubmitting: false,
          jobId: null,
          jobStatus: null,
          jobResult: null,
          executionError: null,
        });
      },

      shouldShowSocialStep: () => {
        const { formData } = get();
        return formData.contentTypes.includes(ContentType.SOCIAL_POST);
      },

      getTotalSteps: () => {
        const showSocial = get().shouldShowSocialStep();
        return showSocial ? 6 : 5;
      },

      isStepValid: (step: number) => {
        const { formData, validationErrors } = get();

        // Check for existing validation errors
        const hasErrors = Object.keys(validationErrors).length > 0;
        if (hasErrors) return false;

        // Step-specific validation
        switch (step) {
          case 0: // Basic Request
            return (
              formData.requestText.length >= 10 &&
              formData.contentTypes.length > 0
            );
          case 1: // Audience & Tone
            return formData.targetAudience.length >= 3;
          case 2: // Social Settings (if applicable)
            if (get().shouldShowSocialStep()) {
              return formData.socialSettings !== undefined;
            }
            return true;
          default:
            return true;
        }
      },
    }),
    { name: 'wizard-store' }
  )
);
