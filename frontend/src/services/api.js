import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Projects API
export const projectsApi = {
  list: () => api.get('/projects'),
  create: (data) => api.post('/projects', data),
  get: (id) => api.get(`/projects/${id}`),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
};

// XML Patterns API
export const patternsApi = {
  save: (projectId, pattern) => api.post(`/projects/${projectId}/pattern`, pattern),
  get: (projectId) => api.get(`/projects/${projectId}/pattern`),
  validate: (pattern) => api.post('/patterns/validate', pattern),
};

// Data Generation API
export const generationApi = {
  generate: (projectId, config) => api.post(`/projects/${projectId}/generate`, config),
  getStatus: (projectId, jobId) => api.get(`/projects/${projectId}/generation/${jobId}`),
  cancel: (projectId, jobId) => api.post(`/projects/${projectId}/generation/${jobId}/cancel`),
};

// Datasets API
export const datasetsApi = {
  list: (projectId) => api.get(`/projects/${projectId}/datasets`),
  get: (projectId, datasetId) => api.get(`/projects/${projectId}/datasets/${datasetId}`),
  validate: (projectId, datasetId) => api.post(`/projects/${projectId}/datasets/${datasetId}/validate`),
  export: (projectId, datasetId, format) => api.get(`/projects/${projectId}/datasets/${datasetId}/export`, {
    params: { format },
    responseType: 'blob',
  }),
  delete: (projectId, datasetId) => api.delete(`/projects/${projectId}/datasets/${datasetId}`),
};

// Training API
export const trainingApi = {
  start: (projectId, config) => api.post(`/projects/${projectId}/train`, config),
  getStatus: (projectId, jobId) => api.get(`/projects/${projectId}/training/${jobId}`),
  stop: (projectId, jobId) => api.post(`/projects/${projectId}/training/${jobId}/stop`),
  getLogs: (projectId, jobId) => api.get(`/projects/${projectId}/training/${jobId}/logs`),
};

// Models API
export const modelsApi = {
  list: (projectId) => api.get(`/projects/${projectId}/models`),
  get: (projectId, modelId) => api.get(`/projects/${projectId}/models/${modelId}`),
  export: (projectId, modelId, format) => api.post(`/projects/${projectId}/models/${modelId}/export`, { format }),
  delete: (projectId, modelId) => api.delete(`/projects/${projectId}/models/${modelId}`),
};

// HuggingFace API
export const huggingfaceApi = {
  searchModels: (query) => api.get('/huggingface/models', { params: { query } }),
};

export default api;
