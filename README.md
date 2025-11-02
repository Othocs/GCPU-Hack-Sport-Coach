# AI Sport Coach - Posture Analysis Pipeline

## Overview
AI Sport Coach is a computer vision-based application that analyzes workout postures in real-time, providing feedback and guidance to users performing various exercises. The system uses MediaPipe for pose estimation and custom analyzers for different exercises.

## Supported Exercises
- Squats
- Push-ups
- Planks
- Deadlifts
- Lunges

## Prerequisites
- Python 3.8+
- pip (Python package manager)
- Webcam or video input source

## Installation

1. Clone the repository:
   ```bash
   git clone [your-repository-url]
   cd GCPU-Hack-Sport-Coach
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Real-time Posture Analysis
Run the main script to start the webcam feed and analyze your posture in real-time:
```bash
python skeletton.py
```

### Using the Gemini API (Optional)
For advanced analysis using Google's Gemini API:
1. Create a `.env` file in the project root
2. Add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
3. Run the Gemini analysis script:
   ```bash
   python gemini_call.py
   ```

## Project Structure
- `posture_analyzer/`: Core posture analysis modules
  - `analyzers/`: Exercise-specific analysis modules (squat, pushup, plank, etc.)
  - `landmarks.py`: Landmark detection and processing
  - `angles.py`: Angle calculations for joint analysis
  - `detect.py`: Main detection pipeline
  - `fatigue.py`: Fatigue detection and analysis
  - `exercise_recognizer.py`: Automatic exercise recognition

  - `summary.py`: Generate analysis summaries
  - `generic.py`: Generic exercise analysis utilities
- `skeletton.py`: Main application script
- `gemini_call.py`: Integration with Google's Gemini API
- `requirements.txt`: Python dependencies


## Features

### Core Functionality
- Real-time pose estimation using MediaPipe
- Exercise-specific form analysis
- Visual feedback on posture
- Performance metrics and repetition counting

### Advanced Analysis
- **Automatic Exercise Recognition**: Detects the type of exercise being performed
- **Fatigue Detection**: Monitors form degradation and muscle fatigue
- **Form Quality Scoring**: Rates the quality of each repetition
- **Joint Angle Analysis**: Tracks joint angles for precise form assessment

### Progress Tracking
- Session history and statistics
- Performance trends over time
- Detailed exercise analytics
- Exportable progress reports

### Integration
- Google Gemini AI for advanced analysis
- Support for multiple users
- Data export in JSON format

## Usage Examples

### Basic Usage
```python
# Initialize the posture analyzer
from posture_analyzer import analyze_generic_exercise, summarize_analysis

# Analyze a frame
analysis = analyze_generic_exercise(landmarks, exercise_type="squat")
print(summarize_analysis(analysis))
```

### Using Advanced Features
```python
from posture_analyzer import FatigueAnalyzer, ExerciseRecognizer

# Initialize components
fatigue_analyzer = FatigueAnalyzer()
exercise_recognizer = ExerciseRecognizer()

# In your video processing loop
while True:
    # Get landmarks from your video feed
    # ...
    
    # Recognize exercise
    exercise, confidence = exercise_recognizer.recognize(landmarks)
    
    # Analyze fatigue
    fatigue_scores = fatigue_analyzer.update(landmarks)
    
    if fatigue_analyzer.is_fatigued():
        print("Warning: Signs of fatigue detected!")
```