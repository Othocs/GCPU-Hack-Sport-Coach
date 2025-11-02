
export interface Mistake {
  issue: string;
  severity: 'severe' | 'moderate' | 'minor';
  fix: string;
}

export interface FatigueDetails {
  shoulder_stability?: number;
  core_stability?: number;
  knee_stability?: number;
  elbow_stability?: number;
  ankle_stability?: number;
  velocity?: number;
  early_fatigue?: number;
}

export interface FatigueAnalysis {
  overall: number;
  warning: boolean;
  details?: FatigueDetails;
}

export interface AnalysisResponse {
  detected: boolean;
  exercise?: string;
  confidence?: number;
  phase?: string;
  angles?: Record<string, number>;
  mistakes?: Mistake[];
  severity?: 'severe' | 'moderate' | 'good';
  fatigue?: FatigueAnalysis;
  error?: string;
}

export interface GeminiFeedbackRequest {
  image: string;
  exercise: string;
  angles: Record<string, number>;
  mistakes: Mistake[];
}

export interface GeminiFeedbackResponse {
  feedback: string;
  exercise: string;
}

export interface ExercisesResponse {
  exercises: string[];
}

export interface HealthResponse {
  status: string;
  models_loaded: boolean;
}

export type ExerciseType = 'squat' | 'pushup' | 'plank' | 'deadlift' | 'lunge';
