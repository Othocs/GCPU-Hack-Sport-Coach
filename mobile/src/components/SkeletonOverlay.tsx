import React from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import Svg, { Circle, Line } from 'react-native-svg';
import { Landmark } from '../types/analysis';

interface SkeletonOverlayProps {
  landmarks: Landmark[];
  severity?: 'severe' | 'moderate' | 'good';
}

const POSE_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 7],
  [0, 4], [4, 5], [5, 6], [6, 8],
  [9, 10],
  [11, 12],
  [11, 23], [23, 24], [24, 12],
  [12, 14], [14, 16],
  [16, 18], [16, 20], [16, 22],
  [18, 20],
  [11, 13], [13, 15],
  [15, 17], [15, 19], [15, 21],
  [17, 19],
  [24, 26], [26, 28],
  [28, 30], [28, 32],
  [30, 32],
  [23, 25], [25, 27],
  [27, 29], [27, 31],
  [29, 31],
];

export const SkeletonOverlay: React.FC<SkeletonOverlayProps> = ({
  landmarks,
  severity = 'good',
}) => {
  if (!landmarks || landmarks.length === 0) {
    return null;
  }

  const { width, height } = Dimensions.get('window');

  const getColor = () => {
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

  const color = getColor();
  const dotColor = color;
  const lineColor = color;

  return (
    <View style={styles.container} pointerEvents="none">
      <Svg width={width} height={height}>
        {POSE_CONNECTIONS.map(([startIdx, endIdx], index) => {
          const start = landmarks[startIdx];
          const end = landmarks[endIdx];

          if (
            start &&
            end &&
            start.visibility > 0.5 &&
            end.visibility > 0.5
          ) {
            return (
              <Line
                key={`line-${index}`}
                x1={start.x * width}
                y1={start.y * height}
                x2={end.x * width}
                y2={end.y * height}
                stroke={lineColor}
                strokeWidth={2}
                strokeOpacity={0.8}
              />
            );
          }
          return null;
        })}

        {landmarks.map((landmark, index) => {
          if (landmark.visibility < 0.5) {
            return null;
          }

          const x = landmark.x * width;
          const y = landmark.y * height;

          return (
            <Circle
              key={`dot-${index}`}
              cx={x}
              cy={y}
              r={4}
              fill={dotColor}
              fillOpacity={0.9}
              stroke="#FFFFFF"
              strokeWidth={1}
            />
          );
        })}
      </Svg>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    zIndex: 1,
  },
});
