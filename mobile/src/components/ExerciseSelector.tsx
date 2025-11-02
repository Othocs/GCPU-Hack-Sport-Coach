
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { ExerciseType } from '../types/analysis';

interface ExerciseSelectorProps {
  selectedExercise: ExerciseType | 'auto';
  onSelect: (exercise: ExerciseType | 'auto') => void;
}

const EXERCISES: Array<{ value: ExerciseType | 'auto'; label: string }> = [
  { value: 'auto', label: 'Auto-Detect' },
  { value: 'squat', label: 'Squat' },
  { value: 'pushup', label: 'Push-up' },
  { value: 'plank', label: 'Plank' },
  { value: 'deadlift', label: 'Deadlift' },
  { value: 'lunge', label: 'Lunge' },
];

export const ExerciseSelector: React.FC<ExerciseSelectorProps> = ({
  selectedExercise,
  onSelect,
}) => {
  return (
    <View style={styles.container}>
      {EXERCISES.map((exercise) => (
        <TouchableOpacity
          key={exercise.value}
          style={[
            styles.button,
            selectedExercise === exercise.value && styles.buttonSelected,
          ]}
          onPress={() => onSelect(exercise.value)}
        >
          <Text
            style={[
              styles.buttonText,
              selectedExercise === exercise.value && styles.buttonTextSelected,
            ]}
          >
            {exercise.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    padding: 12,
  },
  button: {
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#4B5563',
  },
  buttonSelected: {
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
  },
  buttonText: {
    color: '#D1D5DB',
    fontSize: 14,
    fontWeight: '500',
  },
  buttonTextSelected: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
});
