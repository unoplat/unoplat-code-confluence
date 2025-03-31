/**
 * Environment Variables Helper
 * 
 * Provides type-safe access to environment variables with fallbacks.
 */

export const env = {
  /**
   * API Base URL for backend requests
   */
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
}; 