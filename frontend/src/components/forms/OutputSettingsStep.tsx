/**
 * Step 5: Output Settings - Format and document options.
 */

import React from 'react';
import { useWizardStore } from '../../store/wizardStore';
import { OutputFormat } from '../../api/types';

const OUTPUT_FORMAT_OPTIONS = [
  {
    value: OutputFormat.HTML,
    label: 'HTML',
    icon: '🌐',
    desc: 'Web-ready HTML document',
    extension: '.html',
  },
  {
    value: OutputFormat.MARKDOWN,
    label: 'Markdown',
    icon: '📝',
    desc: 'Plain text with formatting',
    extension: '.md',
  },
  {
    value: OutputFormat.DOCX,
    label: 'Word Document',
    icon: '📄',
    desc: 'Microsoft Word format',
    extension: '.docx',
  },
  {
    value: OutputFormat.PDF,
    label: 'PDF',
    icon: '📕',
    desc: 'Portable Document Format',
    extension: '.pdf',
  },
  {
    value: OutputFormat.PPTX,
    label: 'PowerPoint',
    icon: '📊',
    desc: 'Presentation slides',
    extension: '.pptx',
  },
];

export const OutputSettingsStep: React.FC = () => {
  const { formData, updateFormData } = useWizardStore();

  return (
    <div className="space-y-6">
      {/* Output Format */}
      <div>
        <label className="label">
          Output Format <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
          {OUTPUT_FORMAT_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => updateFormData({ outputFormat: option.value })}
              className={`card-selectable ${
                formData.outputFormat === option.value
                  ? 'card-selectable-active'
                  : 'card-selectable-inactive'
              }`}
            >
              <div className="text-2xl mb-2">{option.icon}</div>
              <div className="font-medium text-gray-800">{option.label}</div>
              <div className="text-xs text-gray-500">{option.desc}</div>
              <div className="text-xs text-gray-400 mt-1">{option.extension}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Document Options */}
      <div className="space-y-4">
        <h4 className="font-medium text-gray-800">Document Options</h4>

        <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          <input
            type="checkbox"
            checked={formData.includeMetadata}
            onChange={(e) => updateFormData({ includeMetadata: e.target.checked })}
            className="w-5 h-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <div>
            <span className="font-medium text-gray-800">Include Metadata</span>
            <p className="text-sm text-gray-500">
              Add document metadata (title, author, date, etc.)
            </p>
          </div>
        </label>

        <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          <input
            type="checkbox"
            checked={formData.pageNumbers}
            onChange={(e) => updateFormData({ pageNumbers: e.target.checked })}
            className="w-5 h-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <div>
            <span className="font-medium text-gray-800">Page Numbers</span>
            <p className="text-sm text-gray-500">
              Add page numbers to the document footer
            </p>
          </div>
        </label>
      </div>

      {/* Format-specific info */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-700 mb-2">Format Details</h4>
        {formData.outputFormat === OutputFormat.PPTX && (
          <p className="text-sm text-gray-600">
            PowerPoint files will be generated with one slide per section, using
            your selected brand template colors and fonts.
          </p>
        )}
        {formData.outputFormat === OutputFormat.PDF && (
          <p className="text-sm text-gray-600">
            PDF files will include your brand styling and are optimized for
            printing and sharing.
          </p>
        )}
        {formData.outputFormat === OutputFormat.DOCX && (
          <p className="text-sm text-gray-600">
            Word documents are fully editable and include styled headings,
            paragraphs, and formatting.
          </p>
        )}
        {formData.outputFormat === OutputFormat.HTML && (
          <p className="text-sm text-gray-600">
            HTML output is ready for web publishing with clean, semantic markup.
          </p>
        )}
        {formData.outputFormat === OutputFormat.MARKDOWN && (
          <p className="text-sm text-gray-600">
            Markdown is perfect for documentation, blogs, and version control
            systems.
          </p>
        )}
      </div>
    </div>
  );
};
