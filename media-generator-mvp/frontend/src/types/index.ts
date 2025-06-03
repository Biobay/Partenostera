export interface Project {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  mode: 'tool' | 'veo';
  input_source: string;
  video_path?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  processing_time?: number;
  quality_score?: number;
  sequence_count: number;
}

export interface ProjectDetail extends Project {
  sequences: Sequence[];
  image_paths: string[];
  audio_paths: string[];
  validation_result?: ValidationResult;
}

export interface Sequence {
  id: number;
  text: string;
  summary: string;
  characters: string[];
  location: string;
  time_period: string;
  emotions: string[];
  action_level: number;
}

export interface ValidationResult {
  is_valid: boolean;
  quality_score: number;
  issues: string[];
  warnings: string[];
  processing_time: number;
}

export interface Book {
  id: string;
  title: string;
  author: string;
  description: string;
  language: string;
  word_count: number;
  file_path: string;
  cover_image?: string;
}

export interface GenerationRequest {
  text?: string;
  book_id?: string;
  mode: 'tool' | 'veo';
  custom_text?: string;
}

export interface GenerationStatus {
  project_id: string;
  status: string;
  progress: number;
  current_step: string;
  estimated_time_remaining?: number;
  error_message?: string;
  video_path?: string;
  quality_score?: number;
  validation_result?: ValidationResult;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface SystemConfig {
  max_file_size: string;
  supported_formats: string[];
  max_sequences: number;
}
