/**
 * Step 6: Review & Submit - Summary of all selections before submission.
 */

import React from 'react';
import { useWizardStore } from '../../store/wizardStore';
import { ContentType } from '../../api/types';

const CONTENT_TYPE_LABELS: Record<ContentType, string> = {
  [ContentType.ARTICLE]: 'Article',
  [ContentType.BLOG_POST]: 'Blog Post',
  [ContentType.SOCIAL_POST]: 'Social Post',
  [ContentType.PRESENTATION]: 'Presentation',
  [ContentType.EMAIL]: 'Email',
  [ContentType.NEWSLETTER]: 'Newsletter',
  [ContentType.VIDEO_SCRIPT]: 'Video Script',
  [ContentType.WHITEPAPER]: 'Whitepaper',
  [ContentType.CASE_STUDY]: 'Case Study',
};

interface SectionProps {
  title: string;
  onEdit: () => void;
  children: React.ReactNode;
}

const ReviewSection: React.FC<SectionProps> = ({ title, onEdit, children }) => (
  <div className="border rounded-lg overflow-hidden">
    <div className="bg-gray-50 px-4 py-2 flex justify-between items-center border-b">
      <h4 className="font-medium text-gray-700">{title}</h4>
      <button
        type="button"
        onClick={onEdit}
        className="text-sm text-primary-600 hover:text-primary-700"
      >
        Edit
      </button>
    </div>
    <div className="p-4 space-y-2">{children}</div>
  </div>
);

const ReviewItem: React.FC<{ label: string; value: React.ReactNode }> = ({
  label,
  value,
}) => (
  <div className="flex justify-between">
    <span className="text-gray-500">{label}</span>
    <span className="text-gray-800 font-medium">{value}</span>
  </div>
);

export const ReviewSubmitStep: React.FC = () => {
  const { formData, setCurrentStep, shouldShowSocialStep } = useWizardStore();
  const showSocial = shouldShowSocialStep();

  // Calculate step indices based on whether social step is shown
  const stepIndices = {
    basic: 0,
    audience: 1,
    social: showSocial ? 2 : -1,
    brand: showSocial ? 3 : 2,
    output: showSocial ? 4 : 3,
  };

  return (
    <div className="space-y-6">
      <p className="text-gray-600">
        Review your selections below. Click "Edit" to make changes, or "Submit"
        to start content generation.
      </p>

      {/* Basic Request */}
      <ReviewSection
        title="Content Request"
        onEdit={() => setCurrentStep(stepIndices.basic)}
      >
        <div className="mb-3">
          <span className="text-gray-500 text-sm">Request:</span>
          <p className="text-gray-800 mt-1 bg-gray-50 p-2 rounded">
            {formData.requestText}
          </p>
        </div>
        <ReviewItem
          label="Content Types"
          value={formData.contentTypes
            .map((t) => CONTENT_TYPE_LABELS[t])
            .join(', ')}
        />
        <ReviewItem
          label="Priority"
          value={formData.priority.charAt(0).toUpperCase() + formData.priority.slice(1)}
        />
        {formData.deadline && (
          <ReviewItem
            label="Deadline"
            value={new Date(formData.deadline).toLocaleString()}
          />
        )}
      </ReviewSection>

      {/* Audience & Tone */}
      <ReviewSection
        title="Audience & Tone"
        onEdit={() => setCurrentStep(stepIndices.audience)}
      >
        <ReviewItem label="Target Audience" value={formData.targetAudience} />
        <ReviewItem
          label="Tone"
          value={formData.tone.charAt(0).toUpperCase() + formData.tone.slice(1)}
        />
        {formData.wordCountMin && formData.wordCountMax && (
          <ReviewItem
            label="Word Count"
            value={`${formData.wordCountMin} - ${formData.wordCountMax}`}
          />
        )}
      </ReviewSection>

      {/* Social Settings */}
      {showSocial && formData.socialSettings && (
        <ReviewSection
          title="Platform Settings"
          onEdit={() => setCurrentStep(stepIndices.social)}
        >
          <ReviewItem
            label="Platform"
            value={
              formData.socialSettings.platform.charAt(0).toUpperCase() +
              formData.socialSettings.platform.slice(1)
            }
          />
          <ReviewItem
            label="Format"
            value={
              formData.socialSettings.formatType.charAt(0).toUpperCase() +
              formData.socialSettings.formatType.slice(1)
            }
          />
          <ReviewItem
            label="Include CTA"
            value={formData.socialSettings.includeCta ? 'Yes' : 'No'}
          />
          <ReviewItem
            label="Emoji Usage"
            value={
              formData.socialSettings.emojiDensity.charAt(0).toUpperCase() +
              formData.socialSettings.emojiDensity.slice(1)
            }
          />
        </ReviewSection>
      )}

      {/* Brand Template */}
      <ReviewSection
        title="Brand Template"
        onEdit={() => setCurrentStep(stepIndices.brand)}
      >
        <ReviewItem
          label="Template"
          value={
            formData.brandTemplate.charAt(0).toUpperCase() +
            formData.brandTemplate.slice(1)
          }
        />
      </ReviewSection>

      {/* Output Settings */}
      <ReviewSection
        title="Output Settings"
        onEdit={() => setCurrentStep(stepIndices.output)}
      >
        <ReviewItem
          label="Format"
          value={formData.outputFormat.toUpperCase()}
        />
        <ReviewItem
          label="Include Metadata"
          value={formData.includeMetadata ? 'Yes' : 'No'}
        />
        <ReviewItem
          label="Page Numbers"
          value={formData.pageNumbers ? 'Yes' : 'No'}
        />
      </ReviewSection>

      {/* Ready message */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
        <p className="text-green-700 font-medium">
          Ready to generate your content!
        </p>
        <p className="text-green-600 text-sm mt-1">
          Click "Submit" below to start the workflow.
        </p>
      </div>
    </div>
  );
};
