/**
 * Step 3: Social Settings - Platform-specific settings for social posts.
 */

import React from 'react';
import { useWizardStore } from '../../store/wizardStore';
import { Platform } from '../../api/types';

const PLATFORM_OPTIONS = [
  {
    value: Platform.LINKEDIN,
    label: 'LinkedIn',
    icon: '💼',
    desc: 'Professional networking',
    maxLength: 3000,
  },
  {
    value: Platform.TWITTER,
    label: 'X (Twitter)',
    icon: '🐦',
    desc: 'Microblogging',
    maxLength: 280,
  },
  {
    value: Platform.INSTAGRAM,
    label: 'Instagram',
    icon: '📸',
    desc: 'Visual storytelling',
    maxLength: 2200,
  },
  {
    value: Platform.FACEBOOK,
    label: 'Facebook',
    icon: '👍',
    desc: 'Social networking',
    maxLength: 63206,
  },
];

const FORMAT_OPTIONS = [
  { value: 'single', label: 'Single Post', desc: 'One standalone post' },
  { value: 'thread', label: 'Thread', desc: 'Multi-part series (Twitter only)' },
  { value: 'carousel', label: 'Carousel', desc: 'Multi-slide content' },
];

const EMOJI_OPTIONS = [
  { value: 'none', label: 'None', desc: 'No emojis' },
  { value: 'low', label: 'Low', desc: 'Minimal emoji usage' },
  { value: 'moderate', label: 'Moderate', desc: 'Balanced emoji usage' },
  { value: 'high', label: 'High', desc: 'Frequent emoji usage' },
];

export const SocialSettingsStep: React.FC = () => {
  const { formData, updateFormData } = useWizardStore();
  const settings = formData.socialSettings;

  const updateSocialSettings = (
    updates: Partial<NonNullable<typeof formData.socialSettings>>
  ) => {
    updateFormData({
      socialSettings: {
        ...settings!,
        ...updates,
      },
    });
  };

  if (!settings) {
    return (
      <div className="text-center py-8 text-gray-500">
        Social settings not initialized. Please go back and select Social Post.
      </div>
    );
  }

  const selectedPlatform = PLATFORM_OPTIONS.find(
    (p) => p.value === settings.platform
  );

  return (
    <div className="space-y-6">
      {/* Platform Selection */}
      <div>
        <label className="label">
          Platform <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 gap-3">
          {PLATFORM_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => updateSocialSettings({ platform: option.value })}
              className={`card-selectable ${
                settings.platform === option.value
                  ? 'card-selectable-active'
                  : 'card-selectable-inactive'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="text-xl">{option.icon}</span>
                <div>
                  <div className="font-medium text-gray-800">{option.label}</div>
                  <div className="text-xs text-gray-500">{option.desc}</div>
                </div>
              </div>
              <div className="text-xs text-gray-400 mt-2">
                Max: {option.maxLength.toLocaleString()} chars
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Format Type */}
      <div>
        <label className="label">Post Format</label>
        <div className="grid grid-cols-3 gap-3">
          {FORMAT_OPTIONS.map((option) => {
            const isDisabled =
              option.value === 'thread' && settings.platform !== Platform.TWITTER;
            return (
              <button
                key={option.value}
                type="button"
                onClick={() =>
                  updateSocialSettings({
                    formatType: option.value as 'single' | 'thread' | 'carousel',
                  })
                }
                disabled={isDisabled}
                className={`card-selectable ${
                  settings.formatType === option.value
                    ? 'card-selectable-active'
                    : isDisabled
                      ? 'opacity-50 cursor-not-allowed border-gray-200'
                      : 'card-selectable-inactive'
                }`}
              >
                <div className="font-medium text-gray-800">{option.label}</div>
                <div className="text-xs text-gray-500">{option.desc}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Emoji Density */}
      <div>
        <label className="label">Emoji Usage</label>
        <select
          value={settings.emojiDensity}
          onChange={(e) =>
            updateSocialSettings({
              emojiDensity: e.target.value as 'none' | 'low' | 'moderate' | 'high',
            })
          }
          className="input-field"
        >
          {EMOJI_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label} - {option.desc}
            </option>
          ))}
        </select>
      </div>

      {/* Include CTA */}
      <div>
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={settings.includeCta}
            onChange={(e) => updateSocialSettings({ includeCta: e.target.checked })}
            className="w-5 h-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <div>
            <span className="font-medium text-gray-800">Include Call-to-Action</span>
            <p className="text-sm text-gray-500">
              Add a compelling CTA at the end of the post
            </p>
          </div>
        </label>
      </div>

      {/* Platform-specific tips */}
      {selectedPlatform && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-800 mb-2">
            {selectedPlatform.icon} {selectedPlatform.label} Tips
          </h4>
          <ul className="text-sm text-blue-700 space-y-1">
            {settings.platform === Platform.LINKEDIN && (
              <>
                <li>Use professional language and industry keywords</li>
                <li>3-5 hashtags recommended</li>
                <li>Optimal length: 150-300 characters</li>
              </>
            )}
            {settings.platform === Platform.TWITTER && (
              <>
                <li>Keep it concise and punchy</li>
                <li>1-2 relevant hashtags</li>
                <li>Threads work great for detailed topics</li>
              </>
            )}
            {settings.platform === Platform.INSTAGRAM && (
              <>
                <li>Lead with a hook in the first line</li>
                <li>5-15 hashtags for discovery</li>
                <li>Emojis are encouraged</li>
              </>
            )}
            {settings.platform === Platform.FACEBOOK && (
              <>
                <li>Conversational tone works best</li>
                <li>1-3 hashtags maximum</li>
                <li>Questions drive engagement</li>
              </>
            )}
          </ul>
        </div>
      )}
    </div>
  );
};
