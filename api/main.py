"""
FastAPI backend for posture analysis
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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from posture_analyzer.pose_detector import PoseDetector
from posture_analyzer.exercise_recognizer import ExerciseRecognizer
from posture_analyzer.analyzers import squat, pushup, plank, deadlift, lunge
from posture_analyzer.fatigue import FatigueAnalyzer
from gemini_call import call_gemini
from gemini_prompt import GEMINI_PROMPT

app = FastAPI(title="Posture Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pose_detector = None
exercise_recognizer = None
fatigue_analyzer = None

EXERCISE_ANALYZERS = {
    'squat': squat.analyze_squat,
    'pushup': pushup.analyze_pushup,
    'plank': plank.analyze_plank,
    'deadlift': deadlift.analyze_deadlift,
    'lunge': lunge.analyze_lunge,
}

class AnalyzeRequest(BaseModel):
    image: str
    exercise: Optional[str] = None

class GeminiFeedbackRequest(BaseModel):
    image: str
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
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]

        image_bytes = base64.b64decode(base64_string)
        pil_image = Image.open(BytesIO(image_bytes))
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")


@app.post("/api/analyze")
async def analyze_posture(request: AnalyzeRequest):
    """Analyze posture from a single frame"""

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
        if not request.image or len(request.image.strip()) == 0:
            raise HTTPException(status_code=400, detail="Image data is empty")

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

        if frame is None or frame.size == 0:
            raise HTTPException(status_code=400, detail="Decoded image is empty")

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
            exercise_name = "unknown"
            confidence = 0.0
            phase = "unknown"

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

        fatigue_scores = {"overall": 0.0}
        try:
            if fatigue_analyzer:
                result = fatigue_analyzer.analyze(landmarks)
                if result and isinstance(result, dict):
                    fatigue_scores = result
        except Exception as e:
            print(f"Fatigue analysis error: {type(e).__name__}: {str(e)}")

        landmarks_data = []
        if landmarks:
            for landmark in landmarks:
                landmarks_data.append({
                    "x": float(landmark.x),
                    "y": float(landmark.y),
                    "z": float(landmark.z),
                    "visibility": float(landmark.visibility) if hasattr(landmark, 'visibility') else 1.0
                })

        response = {
            "detected": True,
            "exercise": exercise_name if exercise_name else "unknown",
            "confidence": float(confidence) if confidence is not None else 0.0,
            "phase": phase if phase else "unknown",
            "landmarks": landmarks_data,
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
    """Get detailed AI coaching feedback from Gemini"""
    try:
        frame = base64_to_image(request.image)

        context_text = f"Exercise: {request.exercise}\n"
        context_text += f"Angles: {request.angles}\n"
        context_text += f"Issues: {[m['issue'] for m in request.mistakes]}\n"

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
    """Alternative endpoint for uploading files directly"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        landmarks = pose_detector.detect(frame)

        if landmarks is None:
            return {"error": "No pose detected", "detected": False}

        exercise_name, confidence, phase = exercise_recognizer.recognize(
            landmarks,
            frame.shape
        )

        analysis_result = {"angles": {}, "mistakes": [], "severity": "good"}
        if exercise_name in EXERCISE_ANALYZERS:
            analysis_result = EXERCISE_ANALYZERS[exercise_name](landmarks)

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
