# Bug Fix: HTTP 500 Errors

## Problem Summary

The mobile app was experiencing repeated HTTP 500 errors when trying to analyze frames:
```
ERROR  Analysis error: [AxiosError: Request failed with status code 500]
```

## Root Causes Identified

1. **No startup error handling** - Model initialization failures crashed silently
2. **Missing validation** - Invalid/malformed data caused uncaught exceptions
3. **Null handling gaps** - FatigueAnalyzer and other components could return None
4. **Poor error messages** - Hard to debug what went wrong
5. **Cascading failures** - One component failure took down entire request

## Fixes Implemented

### 1. Startup Error Handling (`api/main.py:64-100`)

**Before:**
```python
@app.on_event("startup")
async def startup_event():
    pose_detector = PoseDetector()  # CRASH if model missing
    exercise_recognizer = ExerciseRecognizer()
    fatigue_analyzer = FatigueAnalyzer()
```

**After:**
```python
@app.on_event("startup")
async def startup_event():
    try:
        pose_detector = PoseDetector()
        print("✓ Pose Detector loaded successfully")
        # ... load other models ...
        print("🚀 API Ready! All models loaded successfully")
    except FileNotFoundError as e:
        print("❌ ERROR: Model file not found!")
        print("💡 Solution: Download pose_landmarker_lite.task")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize models!")
        traceback.print_exc()
```

**Benefits:**
- API starts even if models fail
- Clear error messages with solutions
- Full stack traces for debugging

### 2. Improved Health Check (`api/main.py:103-118`)

**Before:**
```python
return {"status": "healthy", "models_loaded": pose_detector is not None}
```

**After:**
```python
return {
    "status": "healthy" if all_loaded else "degraded",
    "models_loaded": all_loaded,
    "models": {
        "pose_detector": pose_detector is not None,
        "exercise_recognizer": exercise_recognizer is not None,
        "fatigue_analyzer": fatigue_analyzer is not None,
    },
    "message": "All systems operational" if all_loaded else "Some models failed to load"
}
```

**Benefits:**
- See exactly which models failed
- Distinguish between healthy and degraded
- Easy to diagnose startup issues

### 3. Comprehensive Request Validation (`api/main.py:150-294`)

**Added validations:**

#### A. Model Availability Check
```python
if pose_detector is None:
    raise HTTPException(503, "Pose detection unavailable - model not loaded")

if exercise_recognizer is None or fatigue_analyzer is None:
    raise HTTPException(503, "Analysis services unavailable - models not loaded")
```

#### B. Input Validation
```python
if not request.image or len(request.image.strip()) == 0:
    raise HTTPException(400, "Image data is empty")
```

#### C. Image Decoding with Specific Errors
```python
try:
    frame = base64_to_image(request.image)
except HTTPException:
    raise  # Re-raise 400 errors
except Exception as e:
    print(f"Image decoding error: {type(e).__name__}: {str(e)}")
    raise HTTPException(400, f"Failed to decode image: {type(e).__name__}")
```

#### D. Pose Detection Error Handling
```python
try:
    landmarks = pose_detector.detect(frame)
except Exception as e:
    print(f"Pose detection error: {type(e).__name__}: {str(e)}")
    traceback.print_exc()
    raise HTTPException(500, f"Pose detection failed: {type(e).__name__}")
```

#### E. Graceful Degradation for Non-Critical Components
```python
# Exercise recognition - continue if fails
try:
    exercise_name, confidence, phase = exercise_recognizer.recognize(landmarks, frame.shape)
except Exception as e:
    print(f"Exercise recognition error: {type(e).__name__}: {str(e)}")
    exercise_name = "unknown"  # Continue with unknown

# Exercise analysis - continue if fails
try:
    analysis_result = EXERCISE_ANALYZERS[exercise_name](landmarks)
except Exception as e:
    print(f"Exercise analysis error: {type(e).__name__}: {str(e)}")
    traceback.print_exc()
    # Continue with empty analysis

# Fatigue analysis - continue if fails
try:
    if fatigue_analyzer:
        result = fatigue_analyzer.analyze(landmarks)
        if result and isinstance(result, dict):
            fatigue_scores = result
except Exception as e:
    print(f"Fatigue analysis error: {type(e).__name__}: {str(e)}")
    # Continue with default scores
```

**Benefits:**
- Partial failures don't break entire request
- Non-critical features degrade gracefully
- Core pose detection still works even if analysis fails

#### F. Enhanced Error Messages
```python
except Exception as e:
    print(f"Unexpected error: {type(e).__name__}: {str(e)}")
    traceback.print_exc()
    raise HTTPException(
        500,
        f"Internal server error: {type(e).__name__}. Check server logs for details."
    )
```

**Benefits:**
- Error type included in response
- Full stack trace logged to console
- Clear direction to check logs

### 4. Detailed Logging Throughout Pipeline

Every step now logs errors:
- Image decoding: `Image decoding error: <type>: <message>`
- Pose detection: `Pose detection error: <type>: <message>`
- Exercise recognition: `Exercise recognition error: <type>: <message>`
- Exercise analysis: `Exercise analysis error (<exercise>): <type>: <message>`
- Fatigue analysis: `Fatigue analysis error: <type>: <message>`

## Testing the Fixes

### 1. Verify Startup

```bash
# Start backend
uv run python start_backend_ngrok.py

# Look for success messages:
# ✓ Pose Detector loaded successfully
# ✓ Exercise Recognizer loaded successfully
# ✓ Fatigue Analyzer loaded successfully
# 🚀 API Ready! All models loaded successfully
```

### 2. Check Health Endpoint

```bash
curl http://localhost:8000/health | jq
```

**Expected Response (healthy):**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "models": {
    "pose_detector": true,
    "exercise_recognizer": true,
    "fatigue_analyzer": true
  },
  "message": "All systems operational"
}
```

**If degraded:**
```json
{
  "status": "degraded",
  "models_loaded": false,
  "models": {
    "pose_detector": false,  // Which model failed
    "exercise_recognizer": true,
    "fatigue_analyzer": true
  },
  "message": "Some models failed to load"
}
```

### 3. Test Mobile App

1. Start backend with ngrok
2. Update mobile/.env with ngrok URL
3. Start mobile app
4. Try analyzing frames
5. Check backend console for detailed logs

### 4. Monitor Backend Logs

Watch for these log patterns:

**Success:**
```
✓ Pose Detector loaded successfully
```

**Errors (now caught and logged):**
```
❌ ERROR: Model file not found!
💡 Solution: Download pose_landmarker_lite.task

Image decoding error: ValueError: Invalid base64
Pose detection error: AttributeError: 'NoneType' object has no attribute 'detect'
Exercise analysis error (squat): TypeError: unsupported operand type(s)
```

## Common Scenarios Now Handled

| Scenario | Before | After |
|----------|--------|-------|
| Model file missing | 500 on first request | Clear startup error with solution |
| Invalid base64 | 500 with cryptic message | 400 with "Failed to decode image" |
| Empty image | 500 | 400 with "Image data is empty" |
| No pose detected | 200 with error | 200 with helpful hint |
| Analyzer crashes | 500, entire request fails | Continues with empty analysis |
| Fatigue analysis fails | 500 | Continues with default scores |
| Network issues | Generic 500 | Specific error type in logs |

## What to Check If Still Getting 500 Errors

1. **Check Backend Console**
   - Look for stack traces
   - Check which component is failing
   - Note the error type (AttributeError, TypeError, etc.)

2. **Verify Model File**
   ```bash
   ls -la pose_landmarker_lite.task
   ```
   Should be ~5.5MB

3. **Test Health Endpoint**
   ```bash
   curl http://localhost:8000/health
   ```
   Should show all models loaded

4. **Check Dependencies**
   ```bash
   uv sync  # Reinstall if needed
   ```

5. **Test with Simple Image**
   - Try with a clear, well-lit photo first
   - Verify person is fully visible

6. **Check Ngrok Connection**
   - Verify URL is correct in mobile/.env
   - Check ngrok hasn't expired (~2 hours)

## Error Response Format

The API now returns clear error responses:

**400 - Bad Request (client error):**
```json
{
  "detail": "Image data is empty"
}
```

**500 - Internal Server Error:**
```json
{
  "detail": "Internal server error: AttributeError. Check server logs for details."
}
```

**503 - Service Unavailable:**
```json
{
  "detail": "Pose detection unavailable - model not loaded. Check server logs."
}
```

## Next Steps If Issues Persist

If you still see 500 errors after these fixes:

1. Share the **full error message** from backend console
2. Note what **action triggered** the error (startup, first request, etc.)
3. Check if error is **consistent** or intermittent
4. Try the **health endpoint** to see model status

The enhanced logging will now show exactly where the failure occurs!
