import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  Project, 
  User, 
  BookCatalogItem, 
  TextChunk, 
  ValidationResult, 
  ApiResponse,
  UploadProgress,
  Scene
} from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor per gestire errori globali
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  // User Management
  async getUsers(): Promise<User[]> {
    const response: AxiosResponse<ApiResponse<User[]>> = await this.api.get('/users');
    return response.data.data || [];
  }

  async getUserById(id: string): Promise<User | null> {
    const response: AxiosResponse<ApiResponse<User>> = await this.api.get(`/users/${id}`);
    return response.data.data || null;
  }

  // Project Management
  async createProject(projectData: {
    userId: string;
    title: string;
    description: string;
    textContent: string;
  }): Promise<Project> {
    const response: AxiosResponse<ApiResponse<Project>> = await this.api.post('/projects', projectData);
    return response.data.data!;
  }

  async getProjects(userId?: string): Promise<Project[]> {
    const url = userId ? `/projects?userId=${userId}` : '/projects';
    const response: AxiosResponse<ApiResponse<Project[]>> = await this.api.get(url);
    return response.data.data || [];
  }
  async getProjectById(id: string): Promise<Project | null> {
    const response: AxiosResponse<ApiResponse<Project>> = await this.api.get(`/projects/${id}`);
    return response.data.data || null;
  }

  // Alias for consistency with ProjectDetail component
  async getProject(id: string): Promise<ApiResponse<Project>> {
    const response: AxiosResponse<ApiResponse<Project>> = await this.api.get(`/projects/${id}`);
    return response.data;
  }

  async updateProject(id: string, updates: Partial<Project>): Promise<Project> {
    const response: AxiosResponse<ApiResponse<Project>> = await this.api.put(`/projects/${id}`, updates);
    return response.data.data!;
  }

  async deleteProject(id: string): Promise<void> {
    await this.api.delete(`/projects/${id}`);
  }

  // Text Processing
  async uploadTextFile(
    file: File, 
    onProgress?: (progress: UploadProgress) => void
  ): Promise<{ textContent: string; chunks: TextChunk[] }> {
    const formData = new FormData();
    formData.append('file', file);

    const response: AxiosResponse<ApiResponse<{ textContent: string; chunks: TextChunk[] }>> = 
      await this.api.post('/text/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress: UploadProgress = {
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              percentage: Math.round((progressEvent.loaded * 100) / progressEvent.total),
            };
            onProgress(progress);
          }
        },
      });

    return response.data.data!;
  }
  async analyzeText(text: string): Promise<TextChunk[]> {
    const response: AxiosResponse<ApiResponse<TextChunk[]>> = await this.api.post('/text/analyze', { text });
    return response.data.data || [];
  }
  async analyzeTextScenes(text: string): Promise<Scene[]> {
    const response: AxiosResponse<ApiResponse<{ scenes: Scene[] }>> = await this.api.post('/analyze-text', { text });
    return response.data.data?.scenes || [];
  }

  // Image Generation
  async generateImages(projectId: string, chunks: TextChunk[]): Promise<void> {
    await this.api.post(`/projects/${projectId}/generate-images`, { chunks });
  }

  async generateAudio(projectId: string, chunks: TextChunk[]): Promise<void> {
    await this.api.post(`/projects/${projectId}/generate-audio`, { chunks });
  }

  async generateVideo(projectId: string): Promise<void> {
    await this.api.post(`/projects/${projectId}/generate-video`);
  }

  // Validation
  async validateGeneration(projectId: string): Promise<ValidationResult> {
    const response: AxiosResponse<ApiResponse<ValidationResult>> = 
      await this.api.post(`/projects/${projectId}/validate`);
    return response.data.data!;
  }

  // Book Catalog
  async getBookCatalog(): Promise<BookCatalogItem[]> {
    const response: AxiosResponse<ApiResponse<BookCatalogItem[]>> = await this.api.get('/books');
    return response.data.data || [];
  }

  async getBookById(id: string): Promise<BookCatalogItem | null> {
    const response: AxiosResponse<ApiResponse<BookCatalogItem>> = await this.api.get(`/books/${id}`);
    return response.data.data || null;
  }

  async getBookContent(id: string): Promise<string> {
    const response: AxiosResponse<ApiResponse<{ content: string }>> = 
      await this.api.get(`/books/${id}/content`);
    return response.data.data?.content || '';
  }
  // WebSocket per updates in tempo reale
  connectToProject(projectId: string): WebSocket | null {
    if (typeof window !== 'undefined' && 'WebSocket' in window) {
      const wsUrl = `ws://localhost:8000/ws/projects/${projectId}`;
      return new WebSocket(wsUrl);
    }
    return null;
  }

  // Alias for consistency with ProjectDetail component
  connectWebSocket(projectId: string): WebSocket | null {
    return this.connectToProject(projectId);
  }
}

export const apiService = new ApiService();
export default apiService;