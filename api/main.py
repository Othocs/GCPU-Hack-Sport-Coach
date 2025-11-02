"""
FastAPI backend for posture analysis
Wraps the existing posture_analyzer system with REST API endpoints
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import sys
import os

# Add parent directory to path to import posture_analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from posture_analyzer.pose_detector import PoseDetector
from posture_analyzer.exercise_recognizer import ExerciseRecognizer
from posture_analyzer.analyzers import squat, pushup, plank, deadlift, lunge
from posture_analyzer.fatigue import FatigueAnalyzer
from gemini_call import call_gemini
from gemini_prompt import GEMINI_PROMPT

app = FastAPI(title="Posture Analysis API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
pose_detector = None
exercise_recognizer = None
fatigue_analyzer = None

# Exercise analyzer mapping
EXERCISE_ANALYZERS = {
    'squat': squat.analyze_squat,
    'pushup': pushup.analyze_pushup,
    'plank': plank.analyze_plank,
    'deadlift': deadlift.analyze_deadlift,
    'lunge': lunge.analyze_lunge,
}

class AnalyzeRequest(BaseModel):
    image: str  # base64 encoded image
    exercise: Optional[str] = None  # Optional: specify exercise, or auto-detect

class GeminiFeedbackRequest(BaseModel):
    image: str  # base64 encoded image
    exercise: str
    angles: Dict[str, float]
    mistakes: List[Dict[str, str]]


@app.on_event("startup")
async def startup_event():
    """Initialize ML models on startup"""
    global pose_detector, exercise_recognizer, fatigue_analyzer

    try:
        print("Initializing Pose Detector...")
        pose_detector = PoseDetector()
        print("✓ Pose Detector loaded successfully")

        print("Initializing Exercise Recognizer...")
        exercise_recognizer = ExerciseRecognizer()
        print("✓ Exercise Recognizer loaded successfully")

        print("Initializing Fatigue Analyzer...")
        fatigue_analyzer = FatigueAnalyzer()
        print("✓ Fatigue Analyzer loaded successfully")

        print("\n" + "=" * 50)
        print("🚀 API Ready! All models loaded successfully")
        print("=" * 50 + "\n")

    except FileNotFoundError as e:
        print(f"\n❌ ERROR: Model file not found!")
        print(f"Details: {str(e)}")
        print("\n💡 Solution:")
        print("  Download the MediaPipe model file:")
        print("  curl -o pose_landmarker_lite.task https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task")
        print("\nAPI will start but pose detection will not work.")

    except Exception as e:
        print(f"\n❌ ERROR: Failed to initialize models!")
        print(f"Error type: {type(e).__name__}")
        print(f"Details: {str(e)}")
        print("\nAPI will start but may not function correctly.")
        import traceback
        traceback.print_exc()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    models_status = {
        "pose_detector": pose_detector is not None,
        "exercise_recognizer": exercise_recognizer is not None,
        "fatigue_analyzer": fatigue_analyzer is not None,
    }
    all_loaded = all(models_status.values())

    return {
        "status": "healthy" if all_loaded else "degraded",
        "models_loaded": all_loaded,
        "models": models_status,
        "message": "All systems operational" if all_loaded else "Some models failed to load"
    }


@app.get("/api/exercises")
async def get_exercises():
    """List supported exercises"""
    return {
        "exercises": list(EXERCISE_ANALYZERS.keys())
    }


def base64_to_image(base64_string: str) -> np.ndarray:
    """Convert base64 string to OpenCV image"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]

        # Decode base64
        image_bytes = base64.b64decode(base64_string)

        # Convert to PIL Image
        pil_image = Image.open(BytesIO(image_bytes))

        # Convert to OpenCV format (BGR)
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")


@app.post("/api/analyze")
async def analyze_posture(request: AnalyzeRequest):
    """
    Analyze posture from a single frame

    Returns:
    - exercise: detected exercise name
    - confidence: detection confidence
    - phase: exercise phase (init/mid/end)
    - angles: key joint angles
    - mistakes: list of form issues with severity
    - corrections: specific fixes for each mistake
    - fatigue: fatigue metrics
    """

    # Check models are initialized
    if pose_detector is None:
        raise HTTPException(
            status_code=503,
            detail="Pose detection unavailable - model not loaded. Check server logs."
        )

    if exercise_recognizer is None or fatigue_analyzer is None:
        raise HTTPException(
            status_code=503,
            detail="Analysis services unavailable - models not loaded. Check server logs."
        )

    try:
        # Validate input
        if not request.image or len(request.image.strip()) == 0:
            raise HTTPException(status_code=400, detail="Image data is empty")

        # Decode image
        try:
            frame = base64_to_image(request.image)
        except HTTPException:
            raise
        except Exception as e:
            print(f"Image decoding error: {type(e).__name__}: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to decode image: {type(e).__name__}"
            )

        # Validate frame
        if frame is None or frame.size == 0:
            raise HTTPException(status_code=400, detail="Decoded image is empty")

        # Detect pose landmarks
        try:
            landmarks = pose_detector.detect(frame)
        except Exception as e:
            print(f"Pose detection error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Pose detection failed: {type(e).__name__}. Check server logs."
            )

        if landmarks is None:
            return {
                "error": "No pose detected in frame",
                "detected": False,
                "hint": "Ensure person is visible and well-lit"
            }

        # Recognize exercise (or use specified one)
        try:
            if request.exercise:
                exercise_name = request.exercise.lower()
                confidence = 1.0
                phase = "mid"
            else:
                result = exercise_recognizer.recognize(landmarks, frame.shape)
                if result is None or len(result) != 3:
                    exercise_name = "unknown"
                    confidence = 0.0
                    phase = "unknown"
                else:
                    exercise_name, confidence, phase = result
        except Exception as e:
            print(f"Exercise recognition error: {type(e).__name__}: {str(e)}")
            # Continue with unknown exercise
            exercise_name = "unknown"
            confidence = 0.0
            phase = "unknown"

        # Analyze posture for specific exercise
        analysis_result = {"angles": {}, "mistakes": [], "severity": "good"}

        if exercise_name and exercise_name in EXERCISE_ANALYZERS:
            try:
                analysis_result = EXERCISE_ANALYZERS[exercise_name](landmarks)
                if not isinstance(analysis_result, dict):
                    print(f"Warning: Analyzer returned {type(analysis_result)}, expected dict")
                    analysis_result = {"angles": {}, "mistakes": [], "severity": "good"}
            except Exception as e:
                print(f"Exercise analysis error ({exercise_name}): {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                # Continue with empty analysis rather than failing completely

        # Analyze fatigue
        fatigue_scores = {"overall": 0.0}
        try:
            if fatigue_analyzer:
                result = fatigue_analyzer.analyze(landmarks)
                if result and isinstance(result, dict):
                    fatigue_scores = result
        except Exception as e:
            print(f"Fatigue analysis error: {type(e).__name__}: {str(e)}")
            # Continue with default fatigue scores

        # Build response
        response = {
            "detected": True,
            "exercise": exercise_name if exercise_name else "unknown",
            "confidence": float(confidence) if confidence is not None else 0.0,
            "phase": phase if phase else "unknown",
            "angles": analysis_result.get("angles", {}),
            "mistakes": analysis_result.get("mistakes", []),
            "severity": analysis_result.get("severity", "good"),
            "fatigue": {
                "overall": float(fatigue_scores.get("overall", 0.0)),
                "warning": fatigue_scores.get("overall", 0.0) > 0.3,
                "details": {
                    k: float(v) for k, v in fatigue_scores.items() if k != "overall"
                }
            }
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in analyze_posture: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {type(e).__name__}. Check server logs for details."
        )


@app.post("/api/gemini-feedback")
async def get_gemini_feedback(request: GeminiFeedbackRequest):
    """
    Get detailed AI coaching feedback from Gemini

    This is an on-demand endpoint to save API costs
    """
    try:
        # Decode image
        frame = base64_to_image(request.image)

        # Prepare context for Gemini
        context_text = f"Exercise: {request.exercise}\n"
        context_text += f"Angles: {request.angles}\n"
        context_text += f"Issues: {[m['issue'] for m in request.mistakes]}\n"

        # Get Gemini feedback (using existing gemini_call module)
        # Note: This is synchronous - in production, consider async queue
        feedback = call_gemini(
            image_data=frame,
            prompt=GEMINI_PROMPT,
            context=context_text
        )

        return {
            "feedback": feedback,
            "exercise": request.exercise
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini analysis failed: {str(e)}")


@app.post("/api/analyze-stream")
async def analyze_stream(file: UploadFile = File(...)):
    """
    Alternative endpoint for uploading files directly
    Useful for testing and future video upload feature
    """
    try:
        # Read uploaded file
        contents = await file.read()

        # Convert to OpenCV image
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Detect pose landmarks
        landmarks = pose_detector.detect(frame)

        if landmarks is None:
            return {"error": "No pose detected", "detected": False}

        # Recognize exercise
        exercise_name, confidence, phase = exercise_recognizer.recognize(
            landmarks,
            frame.shape
        )

        # Analyze posture
        analysis_result = {"angles": {}, "mistakes": [], "severity": "good"}
        if exercise_name in EXERCISE_ANALYZERS:
            analysis_result = EXERCISE_ANALYZERS[exercise_name](landmarks)

        # Analyze fatigue
        fatigue_scores = fatigue_analyzer.analyze(landmarks)

        return {
            "detected": True,
            "exercise": exercise_name,
            "confidence": float(confidence),
            "phase": phase,
            "angles": analysis_result.get("angles", {}),
            "mistakes": analysis_result.get("mistakes", []),
            "severity": analysis_result.get("severity", "good"),
            "fatigue": {
                "overall": float(fatigue_scores.get("overall", 0.0)),
                "warning": fatigue_scores.get("overall", 0.0) > 0.3
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
