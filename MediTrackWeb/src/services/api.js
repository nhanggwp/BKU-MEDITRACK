// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('auth_token');
  }

  // Set authentication token
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  // Get authentication headers
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (includeAuth && this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Generic API request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getHeaders(options.includeAuth !== false),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // GET request
  async get(endpoint, includeAuth = true) {
    return this.request(endpoint, {
      method: 'GET',
      includeAuth,
    });
  }

  // POST request
  async post(endpoint, data, includeAuth = true) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      includeAuth,
    });
  }

  // PUT request
  async put(endpoint, data, includeAuth = true) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
      includeAuth,
    });
  }

  // DELETE request
  async delete(endpoint, includeAuth = true) {
    return this.request(endpoint, {
      method: 'DELETE',
      includeAuth,
    });
  }
}

export default new ApiService();
