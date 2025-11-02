/**
 * API Client for communicating with the posture analysis backend
 */

import axios, { AxiosInstance } from 'axios';
import {
  AnalysisResponse,
  GeminiFeedbackRequest,
  GeminiFeedbackResponse,
  ExercisesResponse,
  HealthResponse,
} from '../types/analysis';

// Get API URL from environment variable or default to localhost
// Set EXPO_PUBLIC_API_URL in .env file (copy from .env.example)
const DEFAULT_API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

class PostureAPIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = DEFAULT_API_URL) {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Update the API base URL
   */
  setBaseURL(url: string) {
    this.baseURL = url;
    this.client.defaults.baseURL = url;
  }

  /**
   * Get current API base URL
   */
  getBaseURL(): string {
    return this.baseURL;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  /**
   * Get list of supported exercises
   */
  async getExercises(): Promise<string[]> {
    const response = await this.client.get<ExercisesResponse>('/api/exercises');
    return response.data.exercises;
  }

  /**
   * Analyze posture from a base64 image
   * @param imageBase64 Base64 encoded image string
   * @param exercise Optional: specify exercise type, or auto-detect
   */
  async analyzePosture(
    imageBase64: string,
    exercise?: string
  ): Promise<AnalysisResponse> {
    const response = await this.client.post<AnalysisResponse>('/api/analyze', {
      image: imageBase64,
      exercise,
    });
    return response.data;
  }

  /**
   * Get detailed AI coaching feedback from Gemini
   */
  async getGeminiFeedback(
    request: GeminiFeedbackRequest
  ): Promise<GeminiFeedbackResponse> {
    const response = await this.client.post<GeminiFeedbackResponse>(
      '/api/gemini-feedback',
      request
    );
    return response.data;
  }

  /**
   * Check if the API is reachable
   */
  async isReachable(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch (error) {
      console.error('API not reachable:', error);
      return false;
    }
  }
}

// Export singleton instance
export const apiClient = new PostureAPIClient();

// Also export the class for custom instances
export default PostureAPIClient;
