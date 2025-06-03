import axios from 'axios';
import { 
  Project, 
  ProjectDetail, 
  Book, 
  GenerationRequest, 
  GenerationStatus, 
  ApiResponse,
  SystemConfig 
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check
  healthCheck: async (): Promise<{ status: string; timestamp: string }> => {
    const response = await api.get('/health');
    return response.data;
  },

  // System configuration
  getConfig: async (): Promise<SystemConfig> => {
    const response = await api.get('/config');
    return response.data;
  },

  // Books
  getBooks: async (): Promise<Book[]> => {
    const response = await api.get('/books');
    return response.data.books || [];
  },

  // Projects
  getProjects: async (): Promise<Project[]> => {
    const response = await api.get('/projects');
    return response.data.projects || [];
  },

  getProject: async (projectId: string): Promise<ProjectDetail> => {
    const response = await api.get(`/project/${projectId}`);
    return response.data.project;
  },

  deleteProject: async (projectId: string): Promise<void> => {
    await api.delete(`/project/${projectId}`);
  },

  // Generation
  generateMedia: async (request: GenerationRequest & { file?: File }): Promise<{ project_id: string }> => {
    const formData = new FormData();
    
    if (request.file) {
      formData.append('file', request.file);
    }
    
    if (request.book_id) {
      formData.append('book_id', request.book_id);
    }
    
    if (request.custom_text) {
      formData.append('custom_text', request.custom_text);
    }
    
    formData.append('user_mode', request.mode);

    const response = await api.post('/generate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 30000, // 30 seconds for file upload
    });

    return response.data;
  },

  // Generation status
  getGenerationStatus: async (projectId: string): Promise<GenerationStatus> => {
    const response = await api.get(`/generation/status/${projectId}`);
    return response.data;
  },

  // File upload helper
  uploadFile: async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data.filename;
  },
};

export default apiService;
