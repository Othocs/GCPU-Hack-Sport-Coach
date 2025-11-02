
import axios, { AxiosInstance } from 'axios';
import {
  AnalysisResponse,
  GeminiFeedbackRequest,
  GeminiFeedbackResponse,
  ExercisesResponse,
  HealthResponse,
} from '../types/analysis';

const DEFAULT_API_URL = process.env.EXPO_PUBLIC_API_URL || 'http:

class PostureAPIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = DEFAULT_API_URL) {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, 
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  setBaseURL(url: string) {
    this.baseURL = url;
    this.client.defaults.baseURL = url;
  }

  getBaseURL(): string {
    return this.baseURL;
  }

  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  async getExercises(): Promise<string[]> {
    const response = await this.client.get<ExercisesResponse>('/api/exercises');
    return response.data.exercises;
  }

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

  async getGeminiFeedback(
    request: GeminiFeedbackRequest
  ): Promise<GeminiFeedbackResponse> {
    const response = await this.client.post<GeminiFeedbackResponse>(
      '/api/gemini-feedback',
      request
    );
    return response.data;
  }

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

export const apiClient = new PostureAPIClient();

export default PostureAPIClient;
