/**
 * Workout Session Screen
 * Main screen with camera, real-time analysis, and feedback
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Modal,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { FeedbackOverlay } from '../components/FeedbackOverlay';
import { ExerciseSelector } from '../components/ExerciseSelector';
import { apiClient } from '../services/apiClient';
import { captureFrame, FrameThrottler } from '../utils/frameCapture';
import { AnalysisResponse, ExerciseType } from '../types/analysis';

export const WorkoutSession: React.FC = () => {
  const [permission, requestPermission] = useCameraPermissions();
  const [selectedExercise, setSelectedExercise] = useState<ExerciseType | 'auto'>('auto');
  const [isActive, setIsActive] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [geminiModalVisible, setGeminiModalVisible] = useState(false);
  const [geminiFeedback, setGeminiFeedback] = useState<string | null>(null);
  const [isLoadingGemini, setIsLoadingGemini] = useState(false);

  const cameraRef = useRef<CameraView>(null);
  const throttlerRef = useRef(new FrameThrottler(2)); // 2 FPS for POC
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const handlePermissionRequest = async () => {
    const result = await requestPermission();
    if (!result.granted) {
      Alert.alert(
        'Camera Permission Required',
        'Please grant camera access to use posture analysis'
      );
    }
  };

  const startAnalysis = async () => {
    // Check API connectivity first
    const isReachable = await apiClient.isReachable();
    if (!isReachable) {
      Alert.alert(
        'Backend Unreachable',
        'Cannot connect to the posture analysis backend. Please check:\n\n1. Backend is running\n2. Correct API URL is configured\n3. Network connection'
      );
      return;
    }

    setIsActive(true);

    // Start continuous frame capture
    intervalRef.current = setInterval(async () => {
      await analyzeCurrentFrame();
    }, 500); // Check every 500ms, throttler will limit to 2 FPS
  };

  const stopAnalysis = () => {
    setIsActive(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setAnalysis(null);
  };

  const analyzeCurrentFrame = async () => {
    if (!throttlerRef.current.canCall()) {
      return;
    }

    try {
      setIsAnalyzing(true);

      const frameBase64 = await captureFrame(cameraRef, 0.6);
      if (!frameBase64) {
        console.warn('Failed to capture frame');
        return;
      }

      const result = await apiClient.analyzePosture(
        frameBase64,
        selectedExercise === 'auto' ? undefined : selectedExercise
      );

      setAnalysis(result);
    } catch (error) {
      console.error('Analysis error:', error);
      setAnalysis({
        detected: false,
        error: 'Analysis failed',
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGetGeminiFeedback = async () => {
    if (!analysis || !analysis.detected) {
      Alert.alert('No Analysis', 'Please wait for posture detection first');
      return;
    }

    setGeminiModalVisible(true);
    setIsLoadingGemini(true);
    setGeminiFeedback(null);

    try {
      const frameBase64 = await captureFrame(cameraRef, 0.7);
      if (!frameBase64) {
        throw new Error('Failed to capture frame');
      }

      const result = await apiClient.getGeminiFeedback({
        image: frameBase64,
        exercise: analysis.exercise || 'unknown',
        angles: analysis.angles || {},
        mistakes: analysis.mistakes || [],
      });

      setGeminiFeedback(result.feedback);
    } catch (error) {
      console.error('Gemini feedback error:', error);
      Alert.alert('AI Feedback Error', 'Failed to get AI coaching feedback');
      setGeminiModalVisible(false);
    } finally {
      setIsLoadingGemini(false);
    }
  };

  if (!permission) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#3B82F6" />
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <View style={styles.permissionContainer}>
          <Text style={styles.permissionText}>
            Camera access is required for posture analysis
          </Text>
          <TouchableOpacity
            style={styles.permissionButton}
            onPress={handlePermissionRequest}
          >
            <Text style={styles.permissionButtonText}>Grant Permission</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Camera View */}
      <CameraView
        ref={cameraRef}
        style={styles.camera}
        facing="front"
      >
        {/* Feedback Overlay */}
        {isActive && (
          <FeedbackOverlay analysis={analysis} isAnalyzing={isAnalyzing} />
        )}

        {/* Bottom Controls */}
        <View style={styles.bottomContainer}>
          {/* Exercise Selector */}
          {!isActive && (
            <ExerciseSelector
              selectedExercise={selectedExercise}
              onSelect={setSelectedExercise}
            />
          )}

          {/* Control Buttons */}
          <View style={styles.controlsRow}>
            {!isActive ? (
              <TouchableOpacity
                style={styles.startButton}
                onPress={startAnalysis}
              >
                <Text style={styles.startButtonText}>Start Analysis</Text>
              </TouchableOpacity>
            ) : (
              <>
                <TouchableOpacity
                  style={styles.stopButton}
                  onPress={stopAnalysis}
                >
                  <Text style={styles.stopButtonText}>Stop</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={styles.aiButton}
                  onPress={handleGetGeminiFeedback}
                  disabled={!analysis?.detected}
                >
                  <Text style={styles.aiButtonText}>AI Feedback</Text>
                </TouchableOpacity>
              </>
            )}
          </View>
        </View>
      </CameraView>

      {/* Gemini Feedback Modal */}
      <Modal
        visible={geminiModalVisible}
        animationType="slide"
        transparent
        onRequestClose={() => setGeminiModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>AI Coaching Feedback</Text>
              <TouchableOpacity
                onPress={() => setGeminiModalVisible(false)}
                style={styles.closeButton}
              >
                <Text style={styles.closeButtonText}>✕</Text>
              </TouchableOpacity>
            </View>

            {isLoadingGemini ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#3B82F6" />
                <Text style={styles.loadingText}>
                  Getting AI feedback...
                </Text>
              </View>
            ) : (
              <ScrollView style={styles.feedbackScroll}>
                <Text style={styles.feedbackText}>
                  {geminiFeedback || 'No feedback available'}
                </Text>
              </ScrollView>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  camera: {
    flex: 1,
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  permissionText: {
    color: '#FFFFFF',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  permissionButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  permissionButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  bottomContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    paddingBottom: 40,
  },
  controlsRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 12,
    padding: 16,
  },
  startButton: {
    backgroundColor: '#10B981',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
    flex: 1,
    maxWidth: 300,
  },
  startButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
  },
  stopButton: {
    backgroundColor: '#EF4444',
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderRadius: 12,
    flex: 1,
  },
  stopButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  aiButton: {
    backgroundColor: '#8B5CF6',
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderRadius: 12,
    flex: 1,
  },
  aiButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#1F2937',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
    minHeight: '50%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#374151',
  },
  modalTitle: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '600',
  },
  closeButton: {
    padding: 4,
  },
  closeButtonText: {
    color: '#9CA3AF',
    fontSize: 24,
  },
  loadingContainer: {
    padding: 40,
    alignItems: 'center',
  },
  loadingText: {
    color: '#D1D5DB',
    fontSize: 16,
    marginTop: 16,
  },
  feedbackScroll: {
    padding: 20,
  },
  feedbackText: {
    color: '#E5E7EB',
    fontSize: 15,
    lineHeight: 24,
  },
});
