/**
 * Step 2: Audience & Tone - Target audience and content tone settings.
 */

import React from 'react';
import { useWizardStore } from '../../store/wizardStore';
import { ToneType } from '../../api/types';

const TONE_OPTIONS = [
  {
    value: ToneType.PROFESSIONAL,
    label: 'Professional',
    desc: 'Formal, business-appropriate language',
  },
  {
    value: ToneType.CONVERSATIONAL,
    label: 'Conversational',
    desc: 'Friendly, casual, and engaging',
  },
  {
    value: ToneType.TECHNICAL,
    label: 'Technical',
    desc: 'Precise, detailed, jargon-appropriate',
  },
  {
    value: ToneType.PERSUASIVE,
    label: 'Persuasive',
    desc: 'Compelling, action-oriented',
  },
  {
    value: ToneType.EDUCATIONAL,
    label: 'Educational',
    desc: 'Instructive, clear, step-by-step',
  },
  {
    value: ToneType.INSPIRATIONAL,
    label: 'Inspirational',
    desc: 'Motivating, uplifting, visionary',
  },
];

export const AudienceToneStep: React.FC = () => {
  const { formData, updateFormData, validationErrors } = useWizardStore();

  return (
    <div className="space-y-6">
      {/* Target Audience */}
      <div>
        <label className="label">
          Target Audience <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={formData.targetAudience}
          onChange={(e) => updateFormData({ targetAudience: e.target.value })}
          placeholder="e.g., IT executives, healthcare professionals, small business owners"
          className={`input-field ${
            validationErrors.targetAudience ? 'input-error' : ''
          }`}
        />
        {validationErrors.targetAudience && (
          <p className="error-text">{validationErrors.targetAudience}</p>
        )}
        <p className="mt-1 text-sm text-gray-500">
          Describe who will be reading this content
        </p>
      </div>

      {/* Tone Selection */}
      <div>
        <label className="label">
          Content Tone <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 gap-3">
          {TONE_OPTIONS.map((option) => (
            <label
              key={option.value}
              className={`card-selectable flex items-start gap-3 ${
                formData.tone === option.value
                  ? 'card-selectable-active'
                  : 'card-selectable-inactive'
              }`}
            >
              <input
                type="radio"
                name="tone"
                value={option.value}
                checked={formData.tone === option.value}
                onChange={(e) =>
                  updateFormData({ tone: e.target.value as ToneType })
                }
                className="mt-1"
              />
              <div>
                <div className="font-medium text-gray-800">{option.label}</div>
                <div className="text-xs text-gray-500">{option.desc}</div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Word Count Range */}
      <div>
        <label className="label">Word Count Range</label>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Minimum</label>
            <input
              type="number"
              value={formData.wordCountMin || ''}
              onChange={(e) =>
                updateFormData({
                  wordCountMin: e.target.value ? parseInt(e.target.value) : undefined,
                })
              }
              placeholder="e.g., 500"
              min="50"
              max="10000"
              className="input-field"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Maximum</label>
            <input
              type="number"
              value={formData.wordCountMax || ''}
              onChange={(e) =>
                updateFormData({
                  wordCountMax: e.target.value ? parseInt(e.target.value) : undefined,
                })
              }
              placeholder="e.g., 1500"
              min="100"
              max="20000"
              className="input-field"
            />
          </div>
        </div>
        {validationErrors.wordCount && (
          <p className="error-text">{validationErrors.wordCount}</p>
        )}
        <p className="mt-1 text-sm text-gray-500">
          Leave blank to use defaults based on content type
        </p>
      </div>
    </div>
  );
};
