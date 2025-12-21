// API service for FIBO Video Director
// Local development configuration

// Use relative URLs when proxy is configured in package.json
const API_BASE_URL = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:8000';

// Helper function for API requests
const request = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// Health check
export const healthCheck = async () => {
  return request('/');
};

// Generate video plan from script
export const generateVideoPlan = async (scriptText) => {
  console.log('=== API: generateVideoPlan called ===');
  console.log('API_BASE_URL:', API_BASE_URL);
  console.log('Script text length:', scriptText.length);
  
  const result = await request('/api/generate-plan', {
    method: 'POST',
    body: JSON.stringify({ script_text: scriptText }),
  });
  
  console.log('=== API: generateVideoPlan result ===');
  console.log('Result:', result);
  return result;
};

// Get project details
export const getProject = async (projectId) => {
  return request(`/api/project/${projectId}`);
};

// Get checkpoint details
export const getCheckpointPrompts = async (projectId, checkpointId) => {
  return request(`/api/checkpoint/${projectId}/${checkpointId}`);
};

// Generate frames
export const generateFrames = async (projectId, checkpointId, cameraSettings = null) => {
  const requestBody = { 
    project_id: projectId, 
    checkpoint_id: checkpointId 
  };
  
  // Add camera settings if provided
  if (cameraSettings) {
    requestBody.camera_settings = cameraSettings;
  }
  
  return request('/api/generate-frames', {
    method: 'POST',
    body: JSON.stringify(requestBody),
  });
};

// Get generation status
export const getGenerationStatus = async (generationId) => {
  return request(`/api/generation-status/${generationId}`);
};

// Get director mode
export const getDirectorMode = async () => {
  return request('/api/director-mode');
};

// Get cache stats
export const getCacheStats = async () => {
  return request('/api/cache-stats');
};

// Download file
export const downloadFile = async (url, filename) => {
  // Remove leading slash if present to avoid double slashes
  const cleanUrl = url.startsWith('/') ? url.slice(1) : url;
  
  const response = await fetch(`${API_BASE_URL}/${cleanUrl}`, {
    method: 'GET',
  });
  
  if (!response.ok) {
    throw new Error(`Download failed: ${response.status}`);
  }
  
  // Create blob link to download
  const blob = await response.blob();
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

// Default export for backward compatibility
const api = {
  healthCheck,
  generateVideoPlan,
  getProject,
  getCheckpointPrompts,
  generateFrames,
  getGenerationStatus,
  getDirectorMode,
  getCacheStats,
  downloadFile,
  cache
};

export default api;
