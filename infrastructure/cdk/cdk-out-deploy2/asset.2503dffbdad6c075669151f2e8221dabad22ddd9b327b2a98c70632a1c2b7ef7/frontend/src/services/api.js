import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 120000, // 2 minutes for AI generation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    
    if (error.response?.status === 404) {
      throw new Error('Resource not found');
    } else if (error.response?.status === 500) {
      throw new Error('Server error. Please try again later.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please try again.');
    } else {
      throw new Error(error.response?.data?.detail || error.message || 'An error occurred');
    }
  }
);

// API Functions

/**
 * Generate a video plan from a movie script
 * @param {string} scriptText - The movie script text
 * @returns {Promise<Object>} Video plan with checkpoints
 */
export const generateVideoPlan = async (scriptText) => {
  const response = await api.post('/api/generate-plan', {
    script_text: scriptText,
  });
  return response.data;
};

/**
 * Get project details by ID
 * @param {string} projectId - The project ID
 * @returns {Promise<Object>} Project details
 */
export const getProject = async (projectId) => {
  const response = await api.get(`/api/project/${projectId}`);
  return response.data;
};

/**
 * Get FIBO structured prompts for a specific checkpoint
 * @param {string} projectId - The project ID
 * @param {number} checkpointId - The checkpoint ID
 * @returns {Promise<Object>} Checkpoint prompts and data
 */
export const getCheckpointPrompts = async (projectId, checkpointId) => {
  const response = await api.get(`/api/checkpoint/${projectId}/${checkpointId}`);
  return response.data;
};

/**
 * Start frame generation for a checkpoint
 * @param {string} projectId - The project ID
 * @param {number} checkpointId - The checkpoint ID
 * @returns {Promise<Object>} Generation response with generation_id
 */
export const generateFrames = async (projectId, checkpointId) => {
  const response = await api.post('/api/generate-frames', {
    project_id: projectId,
    checkpoint_id: checkpointId,
  });
  return response.data;
};

/**
 * Get the status of frame generation
 * @param {string} generationId - The generation ID
 * @returns {Promise<Object>} Generation status
 */
export const getGenerationStatus = async (generationId) => {
  const response = await api.get(`/api/generation-status/${generationId}`);
  return response.data;
};

/**
 * Download a file from the server
 * @param {string} url - The file URL (relative to API base)
 * @param {string} filename - The desired filename
 */
export const downloadFile = async (url, filename) => {
  // Remove leading slash if present to avoid double slashes
  const cleanUrl = url.startsWith('/') ? url.slice(1) : url;
  
  const response = await api.get(`/${cleanUrl}`, {
    responseType: 'blob',
  });
  
  // Create blob link to download
  const blob = new Blob([response.data]);
  const link = document.createElement('a');
  link.href = window.URL.createObjectURL(blob);
  link.download = filename;
  
  // Trigger download
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // Clean up
  window.URL.revokeObjectURL(link.href);
};

/**
 * Health check endpoint
 * @returns {Promise<Object>} Server status
 */
export const healthCheck = async () => {
  const response = await api.get('/');
  return response.data;
};

// Cache management utilities
export const cache = {
  /**
   * Get cached data
   * @param {string} key - Cache key
   * @returns {any} Cached data or null
   */
  get: (key) => {
    try {
      const item = localStorage.getItem(`fibo_cache_${key}`);
      if (!item) return null;
      
      const parsed = JSON.parse(item);
      
      // Check if expired
      if (parsed.expiry && Date.now() > parsed.expiry) {
        localStorage.removeItem(`fibo_cache_${key}`);
        return null;
      }
      
      return parsed.data;
    } catch (error) {
      console.error('Cache get error:', error);
      return null;
    }
  },

  /**
   * Set cached data
   * @param {string} key - Cache key
   * @param {any} data - Data to cache
   * @param {number} ttl - Time to live in milliseconds (default: 1 hour)
   */
  set: (key, data, ttl = 3600000) => {
    try {
      const item = {
        data,
        expiry: Date.now() + ttl,
      };
      localStorage.setItem(`fibo_cache_${key}`, JSON.stringify(item));
    } catch (error) {
      console.error('Cache set error:', error);
    }
  },

  /**
   * Remove cached data
   * @param {string} key - Cache key
   */
  remove: (key) => {
    try {
      localStorage.removeItem(`fibo_cache_${key}`);
    } catch (error) {
      console.error('Cache remove error:', error);
    }
  },

  /**
   * Clear all cache
   */
  clear: () => {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith('fibo_cache_')) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.error('Cache clear error:', error);
    }
  },
};

export default api;