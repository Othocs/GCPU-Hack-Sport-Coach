
import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { AnalysisResponse } from '../types/analysis';

interface FeedbackOverlayProps {
  analysis: AnalysisResponse | null;
  isAnalyzing: boolean;
}

export const FeedbackOverlay: React.FC<FeedbackOverlayProps> = ({
  analysis,
  isAnalyzing,
}) => {
  if (isAnalyzing) {
    return (
      <View style={styles.container}>
        <View style={styles.statusCard}>
          <Text style={styles.statusText}>Analyzing...</Text>
        </View>
      </View>
    );
  }

  if (!analysis || !analysis.detected) {
    return (
      <View style={styles.container}>
        <View style={[styles.statusCard, styles.errorCard]}>
          <Text style={styles.statusText}>
            {analysis?.error || 'No pose detected'}
          </Text>
          <Text style={styles.helperText}>
            Stand in view of the camera and perform an exercise
          </Text>
        </View>
      </View>
    );
  }

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case 'severe':
        return '#EF4444'; 
      case 'moderate':
        return '#F59E0B'; 
      case 'good':
        return '#10B981'; 
      default:
        return '#6B7280'; 
    }
  };

  const severityColor = getSeverityColor(analysis.severity);

  return (
    <View style={styles.container}>
      {/* Exercise Info */}
      <View style={[styles.exerciseCard, { borderLeftColor: severityColor }]}>
        <Text style={styles.exerciseName}>
          {analysis.exercise?.toUpperCase() || 'Unknown'}
        </Text>
        <View style={styles.row}>
          <Text style={styles.phaseText}>
            Phase: {analysis.phase || 'N/A'}
          </Text>
          <Text style={styles.confidenceText}>
            {Math.round((analysis.confidence || 0) * 100)}%
          </Text>
        </View>
      </View>

      {/* Mistakes */}
      {analysis.mistakes && analysis.mistakes.length > 0 && (
        <ScrollView style={styles.mistakesContainer} bounces={false}>
          {analysis.mistakes.map((mistake, index) => (
            <View
              key={index}
              style={[
                styles.mistakeCard,
                {
                  borderLeftColor:
                    mistake.severity === 'severe'
                      ? '#EF4444'
                      : mistake.severity === 'moderate'
                      ? '#F59E0B'
                      : '#6B7280',
                },
              ]}
            >
              <Text style={styles.mistakeIssue}>{mistake.issue}</Text>
              <Text style={styles.mistakeFix}>{mistake.fix}</Text>
            </View>
          ))}
        </ScrollView>
      )}

      {/* Good Form Indicator */}
      {analysis.severity === 'good' && (
        <View style={[styles.goodFormCard]}>
          <Text style={styles.goodFormText}>✓ Good Form!</Text>
        </View>
      )}

      {/* Fatigue Warning */}
      {analysis.fatigue?.warning && (
        <View style={styles.fatigueWarning}>
          <Text style={styles.fatigueText}>
            ⚠ Fatigue detected - Consider resting
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 60,
    left: 20,
    right: 20,
    maxHeight: '80%',
  },
  statusCard: {
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    padding: 16,
    borderRadius: 12,
  },
  errorCard: {
    backgroundColor: 'rgba(239, 68, 68, 0.9)',
  },
  statusText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  helperText: {
    color: '#E5E7EB',
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
  },
  exerciseCard: {
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    marginBottom: 12,
  },
  exerciseName: {
    color: '#FFFFFF',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  phaseText: {
    color: '#D1D5DB',
    fontSize: 14,
  },
  confidenceText: {
    color: '#10B981',
    fontSize: 16,
    fontWeight: '600',
  },
  mistakesContainer: {
    maxHeight: 300,
  },
  mistakeCard: {
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    marginBottom: 8,
  },
  mistakeIssue: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
  },
  mistakeFix: {
    color: '#D1D5DB',
    fontSize: 12,
  },
  goodFormCard: {
    backgroundColor: 'rgba(16, 185, 129, 0.9)',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  goodFormText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  fatigueWarning: {
    backgroundColor: 'rgba(245, 158, 11, 0.9)',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  fatigueText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
});
