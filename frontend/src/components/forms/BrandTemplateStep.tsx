/**
 * Step 4: Brand Template - Visual template selection with preview.
 */

import React from 'react';
import { useWizardStore } from '../../store/wizardStore';
import { useTemplates } from '../../hooks/useTemplates';
import { BrandTemplate } from '../../api/types';

interface TemplateCardProps {
  template: BrandTemplate;
  isSelected: boolean;
  onSelect: () => void;
}

const TemplateCard: React.FC<TemplateCardProps> = ({
  template,
  isSelected,
  onSelect,
}) => {
  const { colors, typography } = template;

  return (
    <button
      type="button"
      onClick={onSelect}
      className={`card-selectable ${
        isSelected ? 'card-selectable-active' : 'card-selectable-inactive'
      }`}
    >
      {/* Color Preview */}
      <div className="flex gap-1 mb-3">
        <div
          className="w-8 h-8 rounded shadow-sm"
          style={{ backgroundColor: colors.primary }}
          title="Primary"
        />
        <div
          className="w-8 h-8 rounded shadow-sm"
          style={{ backgroundColor: colors.secondary }}
          title="Secondary"
        />
        <div
          className="w-8 h-8 rounded shadow-sm"
          style={{ backgroundColor: colors.accent }}
          title="Accent"
        />
      </div>

      {/* Template Info */}
      <h3 className="font-bold text-gray-800">{template.display_name}</h3>
      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
        {template.description}
      </p>

      {/* Font Preview */}
      <div className="mt-3 p-2 bg-gray-50 rounded text-left">
        <div
          className="text-base font-bold truncate"
          style={{ fontFamily: typography.heading_font }}
        >
          {typography.heading_font}
        </div>
        <div
          className="text-sm text-gray-600 truncate"
          style={{ fontFamily: typography.body_font }}
        >
          Body: {typography.body_font}
        </div>
      </div>

      {/* Selected Indicator */}
      {isSelected && (
        <div className="mt-2 text-center">
          <span className="inline-flex items-center px-2 py-1 text-xs font-medium text-primary-700 bg-primary-100 rounded-full">
            Selected
          </span>
        </div>
      )}
    </button>
  );
};

export const BrandTemplateStep: React.FC = () => {
  const { formData, updateFormData } = useWizardStore();
  const { templates, isLoading, error } = useTemplates();

  const selectedTemplate = templates.find(
    (t) => t.name === formData.brandTemplate
  );

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-2 text-gray-500">Loading templates...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-500">
        <p>Failed to load templates: {error}</p>
        <p className="text-sm mt-2">Using default template.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <p className="text-gray-600">
        Choose a brand template that matches your content style. This affects
        colors, fonts, and overall document styling.
      </p>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map((template) => (
          <TemplateCard
            key={template.name}
            template={template}
            isSelected={formData.brandTemplate === template.name}
            onSelect={() => updateFormData({ brandTemplate: template.name })}
          />
        ))}
      </div>

      {/* Live Preview */}
      {selectedTemplate && (
        <div className="mt-6 border rounded-lg overflow-hidden">
          <div className="bg-gray-100 px-4 py-2 border-b">
            <h4 className="font-medium text-gray-700">Live Preview</h4>
          </div>
          <div
            className="p-6"
            style={{
              backgroundColor: selectedTemplate.colors.background,
              color: selectedTemplate.colors.text,
            }}
          >
            <h3
              className="text-xl font-bold mb-3"
              style={{
                color: selectedTemplate.colors.primary,
                fontFamily: selectedTemplate.typography.heading_font,
              }}
            >
              Sample Heading
            </h3>
            <p
              className="mb-4"
              style={{ fontFamily: selectedTemplate.typography.body_font }}
            >
              This is how your content will look with the{' '}
              <strong>{selectedTemplate.display_name}</strong> brand template.
              Notice the colors, fonts, and overall styling that will be applied
              to your generated documents.
            </p>
            <button
              style={{
                backgroundColor: selectedTemplate.colors.accent,
                color: '#fff',
                padding: '8px 16px',
                borderRadius: '4px',
                fontFamily: selectedTemplate.typography.body_font,
              }}
            >
              Sample Button
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
