export interface User {
  id: string;
  name: string;
  email: string;
  type: 'image_editor' | 'veo_user';
  avatar?: string;
}

export interface Project {
  id: string;
  userId: string;
  title: string;
  description: string;
  status: 'draft' | 'processing' | 'completed' | 'error';
  createdAt: string;
  updatedAt: string;
  textContent: string;
  scenes?: Scene[];
  generatedImages: GeneratedImage[];
  generatedAudio: GeneratedAudio[];
  finalVideo?: GeneratedVideo;
  processingStep?: ProcessingStep;
  progress: number;
}

export interface Scene {
  id: string;
  title: string;
  content: string;
  summary: string;
  chapter_number?: number;
  scene_number?: number;
  characters: string[];
  setting?: string;
  mood?: string;
  themes: string[];
  image_prompt?: string;
  image_generation_status: 'pending' | 'processing' | 'completed' | 'failed';
  image_url?: string;
  image_path?: string;
  image_error?: string;
}

export interface GeneratedImage {
  id: string;
  url: string;
  prompt: string;
  timestamp: number;
  order: number;
  status: 'generating' | 'completed' | 'error';
  validated: boolean;
}

export interface GeneratedAudio {
  id: string;
  url: string;
  text: string;
  duration: number;
  timestamp: number;
  status: 'generating' | 'completed' | 'error';
}

export interface GeneratedVideo {
  id: string;
  url: string;
  duration: number;
  createdAt: string;
  status: 'generating' | 'completed' | 'error';
}

export interface ProcessingStep {
  current: string;
  total: number;
  completed: number;
  currentOperation: string;
}

export interface BookCatalogItem {
  id: string;
  title: string;
  author: string;
  description: string;
  genre: string;
  pages: number;
  coverUrl: string;
  textPreview: string;
}

export interface TextChunk {
  id: string;
  content: string;
  order: number;
  imagePrompt: string;
  audioText: string;
}

export interface ValidationResult {
  isValid: boolean;
  confidence: number;
  issues: string[];
  suggestions: string[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface Book {
  id: string;
  title: string;
  author: string;
  description: string;
  genre: string;
  year: number;
  pages: number;
  language: string;
  coverUrl: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedReadingTime: string;
  tags: string[];
}