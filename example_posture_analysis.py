"""
Example: Using Posture Analyzer with Skeleton Detection

This example shows how to integrate the posture analyzer with
MediaPipe skeleton detection for real-time exercise form analysis.
"""

import cv2
import numpy as np
from skeletton import detect_skeleton, draw_landmarks_on_image
from posture_analyzer import (
    analyze_squat, 
    analyze_pushup, 
    analyze_deadlift,
    analyze_plank,
    analyze_lunge,
    analyze_generic_exercise,
    get_all_angles,
    PoseLandmark
)


def display_analysis_results(frame, analysis_result, x_offset=10, y_offset=30):
    """
    Display analysis results on the frame
    
    Args:
        frame: OpenCV frame
        analysis_result: Dictionary with 'angles', 'mistakes', and 'severity'
        x_offset: X position for text
        y_offset: Starting Y position for text
    """
    y = y_offset
    
    # Display severity
    severity_colors = {
        'good': (0, 255, 0),      # Green
        'moderate': (0, 165, 255),  # Orange
        'severe': (0, 0, 255)       # Red
    }
    severity = analysis_result.get('severity', 'good')
    color = severity_colors.get(severity, (255, 255, 255))
    cv2.putText(frame, f"Severity: {severity.upper()}", 
                (x_offset, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    y += 30
    
    # Display key angles
    angles = analysis_result.get('angles', {})
    if angles:
        cv2.putText(frame, "Key Angles:", 
                    (x_offset, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += 20
        
        # Display first few key angles
        key_angles = list(angles.items())[:3]
        for angle_name, angle_value in key_angles:
            if angle_value is not None:
                cv2.putText(frame, f"{angle_name}: {angle_value:.1f}°", 
                           (x_offset, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                y += 18
    
    # Display mistakes
    mistakes = analysis_result.get('mistakes', [])
    if mistakes:
        y += 10
        cv2.putText(frame, "Detected Issues:", 
                    (x_offset, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        y += 20
        
        for mistake in mistakes[:2]:  # Show first 2 mistakes
            issue = mistake.get('issue', 'Unknown')
            # Truncate long text
            if len(issue) > 40:
                issue = issue[:37] + "..."
            
            severity_color = (0, 0, 255) if mistake.get('severity') == 'severe' else (0, 165, 255)
            cv2.putText(frame, f"- {issue}", 
                       (x_offset, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, severity_color, 1)
            y += 18


def real_time_analysis(exercise_type='squat'):
    """
    Real-time exercise analysis using webcam
    
    Args:
        exercise_type: Type of exercise to analyze (squat, pushup, deadlift, plank, lunge)
    """
    print(f"Starting real-time analysis for: {exercise_type}")
    print("Press 'q' to quit")
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Analysis function mapping
    analysis_functions = {
        'squat': analyze_squat,
        'pushup': analyze_pushup,
        'push-up': analyze_pushup,
        'deadlift': analyze_deadlift,
        'plank': analyze_plank,
        'lunge': analyze_lunge
    }
    
    analyze_func = analysis_functions.get(exercise_type.lower(), analyze_generic_exercise)
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Detect skeleton (process every 2nd frame for performance)
        if frame_count % 2 == 0:
            detection_result = detect_skeleton(frame)
            
            # Analyze posture if landmarks detected
            if detection_result.pose_landmarks and len(detection_result.pose_landmarks) > 0:
                landmarks = detection_result.pose_landmarks[0]
                
                # Perform analysis
                analysis_result = analyze_func(landmarks)
                
                # Display results on frame
                display_analysis_results(frame, analysis_result)
        
        # Draw skeleton
        detection_result = detect_skeleton(frame)
        frame = draw_landmarks_on_image(frame, detection_result)
        
        # Add exercise type label
        cv2.putText(frame, f"Exercise: {exercise_type.upper()}", 
                   (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 2)
        
        cv2.imshow('Exercise Form Analysis', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


def analyze_image(image_path, exercise_type='squat'):
    """
    Analyze exercise form from a single image
    
    Args:
        image_path: Path to image file
        exercise_type: Type of exercise
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return
    
    print(f"Analyzing {exercise_type} in image: {image_path}")
    
    # Detect skeleton
    detection_result = detect_skeleton(image)
    
    if not detection_result.pose_landmarks or len(detection_result.pose_landmarks) == 0:
        print("No pose detected in image")
        return
    
    landmarks = detection_result.pose_landmarks[0]
    
    # Perform analysis
    analysis_functions = {
        'squat': analyze_squat,
        'pushup': analyze_pushup,
        'push-up': analyze_pushup,
        'deadlift': analyze_deadlift,
        'plank': analyze_plank,
        'lunge': analyze_lunge
    }
    
    analyze_func = analysis_functions.get(exercise_type.lower(), analyze_generic_exercise)
    analysis_result = analyze_func(landmarks)
    
    # Display results
    print("\n" + "="*50)
    print("ANALYSIS RESULTS")
    print("="*50)
    print(f"Severity: {analysis_result['severity'].upper()}")
    print("\nAngles:")
    for angle_name, angle_value in analysis_result['angles'].items():
        if angle_value is not None:
            print(f"  {angle_name}: {angle_value:.1f}°")
    
    print("\nDetected Issues:")
    mistakes = analysis_result.get('mistakes', [])
    if mistakes:
        for i, mistake in enumerate(mistakes, 1):
            print(f"\n{i}. {mistake['issue']}")
            print(f"   Severity: {mistake['severity']}")
            print(f"   Fix: {mistake['fix']}")
    else:
        print("  No issues detected!")
    
    # Draw skeleton and display
    annotated_image = draw_landmarks_on_image(image, detection_result)
    display_analysis_results(annotated_image, analysis_result)
    
    cv2.imshow('Exercise Analysis', annotated_image)
    print("\nPress any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    import sys
    
    # Example usage
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "realtime":
            exercise = sys.argv[2] if len(sys.argv) > 2 else "squat"
            real_time_analysis(exercise)
        elif mode == "image":
            image_path = sys.argv[2] if len(sys.argv) > 2 else "image.png"
            exercise = sys.argv[3] if len(sys.argv) > 3 else "squat"
            analyze_image(image_path, exercise)
        else:
            print("Usage:")
            print("  python example_posture_analysis.py realtime [exercise_type]")
            print("  python example_posture_analysis.py image [image_path] [exercise_type]")
            print("\nExercise types: squat, pushup, deadlift, plank, lunge")
    else:
        # Default: analyze image.png
        print("Default: Analyzing image.png as a squat")
        analyze_image("image.png", "squat")
