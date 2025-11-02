# Posture Analysis API

FastAPI backend that wraps the posture analysis system for use with the React Native mobile app.

## Setup

1. Install dependencies with UV:
```bash
# From project root
uv sync
```

This will create a virtual environment in `.venv/` and install all dependencies.

2. Set up environment variables (create `.env` file in project root):
```
GEMINI_API_KEY=your_api_key_here
```

3. Run the API server:
```bash
# From project root
uv run python api/main.py
```

Or with uvicorn directly:
```bash
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true
}
```

### `GET /api/exercises`
List supported exercises

**Response:**
```json
{
  "exercises": ["squat", "pushup", "plank", "deadlift", "lunge"]
}
```

### `POST /api/analyze`
Analyze posture from a single frame

**Request Body:**
```json
{
  "image": "base64_encoded_image_string",
  "exercise": "squat"  // optional, auto-detects if not provided
}
```

**Response:**
```json
{
  "detected": true,
  "exercise": "squat",
  "confidence": 0.85,
  "phase": "mid",
  "angles": {
    "knee_left": 95.0,
    "knee_right": 98.0
  },
  "mistakes": [
    {
      "issue": "Knee Valgus (knees caving inward)",
      "severity": "severe",
      "fix": "Push knees out over toes"
    }
  ],
  "severity": "severe",
  "fatigue": {
    "overall": 0.14,
    "warning": false,
    "details": {
      "shoulder_stability": 0.12,
      "core_stability": 0.08
    }
  }
}
```

### `POST /api/gemini-feedback`
Get detailed AI coaching feedback

**Request Body:**
```json
{
  "image": "base64_encoded_image_string",
  "exercise": "squat",
  "angles": {"knee_left": 95.0},
  "mistakes": [{"issue": "Knee valgus", "severity": "severe"}]
}
```

**Response:**
```json
{
  "feedback": "Detailed biomechanics analysis from Gemini...",
  "exercise": "squat"
}
```

### `POST /api/analyze-stream`
Alternative endpoint for file upload

**Request:** Multipart form data with image file

**Response:** Same as `/api/analyze`

## Testing

Test the API with curl:

```bash
# Health check
curl http://localhost:8000/health

# List exercises
curl http://localhost:8000/api/exercises

# Analyze with base64 image (from mobile app)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_string_here"}'
```

## Notes

- The API processes frames server-side using MediaPipe
- Gemini AI calls are on-demand to save costs
- CORS is enabled for all origins (tighten in production)
- Models are loaded on startup (takes a few seconds)
