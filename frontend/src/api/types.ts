/**
 * TypeScript types matching the FastAPI backend schemas.
 */

export enum ContentType {
  ARTICLE = 'article',
  BLOG_POST = 'blog_post',
  SOCIAL_POST = 'social_post',
  PRESENTATION = 'presentation',
  EMAIL = 'email',
  NEWSLETTER = 'newsletter',
  VIDEO_SCRIPT = 'video_script',
  WHITEPAPER = 'whitepaper',
  CASE_STUDY = 'case_study',
}

export enum ToneType {
  PROFESSIONAL = 'professional',
  CONVERSATIONAL = 'conversational',
  TECHNICAL = 'technical',
  PERSUASIVE = 'persuasive',
  EDUCATIONAL = 'educational',
  INSPIRATIONAL = 'inspirational',
}

export enum Platform {
  LINKEDIN = 'linkedin',
  TWITTER = 'twitter',
  INSTAGRAM = 'instagram',
  FACEBOOK = 'facebook',
}

export enum Priority {
  NORMAL = 'normal',
  HIGH = 'high',
  URGENT = 'urgent',
}

export enum OutputFormat {
  MARKDOWN = 'markdown',
  HTML = 'html',
  DOCX = 'docx',
  PDF = 'pdf',
  PPTX = 'pptx',
}

export enum JobStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

// Form data structure for the wizard
export interface SocialSettings {
  platform: Platform;
  formatType: 'single' | 'thread' | 'carousel';
  includeCta: boolean;
  emojiDensity: 'none' | 'low' | 'moderate' | 'high';
}

export interface WorkflowFormData {
  // Step 1
  requestText: string;
  contentTypes: ContentType[];
  priority: Priority;
  deadline?: string;

  // Step 2
  targetAudience: string;
  tone: ToneType;
  wordCountMin?: number;
  wordCountMax?: number;

  // Step 3 (conditional)
  socialSettings?: SocialSettings;

  // Step 4
  brandTemplate: string;

  // Step 5
  outputFormat: OutputFormat;
  includeMetadata: boolean;
  pageNumbers: boolean;
}

// API response types
export interface StepProgress {
  step: string;
  status: string;
  timestamp: string;
  message?: string;
}

export interface WorkflowStatusResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  current_step?: string;
  steps_completed: StepProgress[];
  estimated_completion?: string;
  error_message?: string;
}

export interface OutputFileInfo {
  file_id: string;
  filename: string;
  format: string;
  size_bytes: number;
  download_url: string;
}

export interface WorkflowResultResponse {
  job_id: string;
  status: JobStatus;
  workflow_type: string;
  success: boolean;
  outputs: OutputFileInfo[];
  content_preview?: string;
  metadata: Record<string, unknown>;
  start_time: string;
  end_time?: string;
  errors: string[];
}

// Template types
export interface ColorPalette {
  primary: string;
  secondary: string;
  accent: string;
  text: string;
  background: string;
}

export interface Typography {
  heading_font: string;
  body_font: string;
  h1_size: number;
  body_size: number;
}

export interface BrandTemplate {
  name: string;
  display_name: string;
  description: string;
  colors: ColorPalette;
  typography: Typography;
  company_name: string;
  preview_image_url?: string;
}

export interface BrandTemplateListResponse {
  templates: BrandTemplate[];
}

// Content type metadata
export interface ContentTypeMetadata {
  id: string;
  name: string;
  display_name: string;
  description: string;
  default_word_count_range: [number, number];
  default_tone: ToneType;
  supports_social_settings: boolean;
  available_output_formats: OutputFormat[];
  icon: string;
}

export interface ContentTypeListResponse {
  content_types: ContentTypeMetadata[];
}

// Platform metadata
export interface PlatformSpec {
  id: string;
  name: string;
  display_name: string;
  max_length: number;
  optimal_length: [number, number];
  hashtag_count: [number, number];
  supports_threads: boolean;
  supports_carousel: boolean;
  emoji_recommendation: string;
  icon: string;
}

export interface PlatformListResponse {
  platforms: PlatformSpec[];
}
