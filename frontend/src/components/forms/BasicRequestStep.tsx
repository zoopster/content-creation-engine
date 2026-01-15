/**
 * Step 1: Basic Request - Content request and type selection.
 */

import React from 'react';
import { useWizardStore } from '../../store/wizardStore';
import { ContentType, Priority } from '../../api/types';

const CONTENT_TYPE_OPTIONS = [
  {
    value: ContentType.ARTICLE,
    label: 'Article',
    icon: '📄',
    desc: 'Long-form editorial content',
  },
  {
    value: ContentType.BLOG_POST,
    label: 'Blog Post',
    icon: '📝',
    desc: 'Informal web content',
  },
  {
    value: ContentType.SOCIAL_POST,
    label: 'Social Post',
    icon: '📱',
    desc: 'Platform-optimized social',
  },
  {
    value: ContentType.PRESENTATION,
    label: 'Presentation',
    icon: '📊',
    desc: 'Slide deck content',
  },
  {
    value: ContentType.EMAIL,
    label: 'Email',
    icon: '📧',
    desc: 'Email communication',
  },
  {
    value: ContentType.NEWSLETTER,
    label: 'Newsletter',
    icon: '📰',
    desc: 'Email newsletter',
  },
  {
    value: ContentType.VIDEO_SCRIPT,
    label: 'Video Script',
    icon: '🎬',
    desc: 'Video narration',
  },
  {
    value: ContentType.WHITEPAPER,
    label: 'Whitepaper',
    icon: '📋',
    desc: 'In-depth technical doc',
  },
  {
    value: ContentType.CASE_STUDY,
    label: 'Case Study',
    icon: '📈',
    desc: 'Success story',
  },
];

export const BasicRequestStep: React.FC = () => {
  const { formData, updateFormData, handleContentTypesChange, validationErrors } =
    useWizardStore();

  const handleRequestTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    updateFormData({ requestText: e.target.value });
  };

  const handleContentTypeToggle = (type: ContentType) => {
    const current = formData.contentTypes;
    const updated = current.includes(type)
      ? current.filter((t) => t !== type)
      : [...current, type];
    handleContentTypesChange(updated);
  };

  return (
    <div className="space-y-6">
      {/* Request Text */}
      <div>
        <label className="label">
          What content do you want to create? <span className="text-red-500">*</span>
        </label>
        <textarea
          value={formData.requestText}
          onChange={handleRequestTextChange}
          placeholder="Describe the content you want to create. For example: 'Write a comprehensive article about cloud migration best practices for IT executives...'"
          className={`input-field h-32 ${
            validationErrors.requestText ? 'input-error' : ''
          }`}
        />
        {validationErrors.requestText && (
          <p className="error-text">{validationErrors.requestText}</p>
        )}
        <p className="mt-1 text-sm text-gray-500">
          {formData.requestText.length}/2000 characters (minimum 10)
        </p>
      </div>

      {/* Content Type Selection */}
      <div>
        <label className="label">
          Select content type(s) <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-3 gap-3">
          {CONTENT_TYPE_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleContentTypeToggle(option.value)}
              className={`card-selectable ${
                formData.contentTypes.includes(option.value)
                  ? 'card-selectable-active'
                  : 'card-selectable-inactive'
              }`}
            >
              <div className="text-2xl mb-1">{option.icon}</div>
              <div className="font-medium text-gray-800">{option.label}</div>
              <div className="text-xs text-gray-500">{option.desc}</div>
            </button>
          ))}
        </div>
        {validationErrors.contentTypes && (
          <p className="error-text">{validationErrors.contentTypes}</p>
        )}
      </div>

      {/* Priority and Deadline Row */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Priority</label>
          <select
            value={formData.priority}
            onChange={(e) =>
              updateFormData({ priority: e.target.value as Priority })
            }
            className="input-field"
          >
            <option value={Priority.NORMAL}>Normal</option>
            <option value={Priority.HIGH}>High</option>
            <option value={Priority.URGENT}>Urgent</option>
          </select>
        </div>

        <div>
          <label className="label">Deadline (optional)</label>
          <input
            type="datetime-local"
            value={formData.deadline || ''}
            onChange={(e) =>
              updateFormData({ deadline: e.target.value || undefined })
            }
            className="input-field"
          />
        </div>
      </div>
    </div>
  );
};
