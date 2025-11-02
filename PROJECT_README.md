# AI Sport Coach - React Native POC

Full-stack mobile application for real-time posture correction during workouts.

## Project Structure

```
GCPU-Hack-Sport-Coach/
├── api/                          # FastAPI Backend
│   ├── main.py                   # API server
│   └── README.md                 # Backend setup guide
├── mobile/                       # React Native App (Expo)
│   ├── src/
│   │   ├── screens/              # Main screens
│   │   ├── components/           # Reusable components
│   │   ├── services/             # API client
│   │   ├── types/                # TypeScript types
│   │   └── utils/                # Utilities
│   ├── App.tsx
│   └── README.md                 # Mobile app setup guide
├── posture_analyzer/             # Core ML Analysis (from vincksi-patch)
│   ├── detect.py                 # MediaPipe pose detection
│   ├── exercise_recognizer.py    # Exercise identification
│   ├── fatigue.py                # Fatigue analysis
│   └── analyzers/                # Exercise-specific analyzers
│       ├── squat.py
│       ├── pushup.py
│       ├── plank.py
│       ├── deadlift.py
│       └── lunge.py
├── gemini_call.py                # Gemini AI integration
├── gemini_prompt.py              # AI coaching prompt
└── requirements.txt              # Python dependencies
```

## Architecture

```
┌─────────────────┐
│  React Native   │  - Camera capture (2 FPS)
│   Mobile App    │  - Real-time UI feedback
│   (iOS/Expo)    │  - Gemini AI requests
└────────┬────────┘
         │ HTTP/JSON (base64 images)
         ↓
┌─────────────────┐
│  FastAPI        │  - Image processing
│   Backend       │  - CORS handling
│  (Python)       │  - Response formatting
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Posture         │  - MediaPipe pose detection
│ Analyzer        │  - Exercise recognition
│ (ML Pipeline)   │  - Form analysis
└────────┬────────┘  - Fatigue monitoring
         │
         ↓
┌─────────────────┐
│ Google Gemini   │  - Advanced AI coaching
│ API (Optional)  │  - Biomechanics expertise
└─────────────────┘  - Natural language feedback
```

## Quick Start

### 1. Backend Setup

```bash
# Install Python dependencies with UV
uv sync

# Set up environment variables
echo "GEMINI_API_KEY=your_key_here" > .env

# Start the API server with ngrok (recommended)
uv run python start_backend_ngrok.py

# The script will display a public URL like:
# ✓ Public URL: https://abc123.ngrok.io
# Copy this URL for the mobile app!
```

**Alternative:** Run without ngrok (local network only)
```bash
uv run python api/main.py
```

### 2. Mobile App Setup

```bash
# Install Node dependencies
cd mobile
npm install

# Create .env file and add the ngrok URL from step 1
cp .env.example .env
# Edit .env and paste: EXPO_PUBLIC_API_URL=https://abc123.ngrok.io

# Start Expo
npm start

# Press 'i' for iOS simulator
```

### 3. Test the Setup

1. Open the mobile app
2. Grant camera permission
3. Tap "Start Analysis"
4. Perform a squat or push-up
5. See real-time feedback!

## Features

### ✅ Implemented (POC)

- **Real-time Posture Detection**: MediaPipe-based skeleton tracking
- **5 Exercise Types**: Squat, Push-up, Plank, Deadlift, Lunge
- **Auto-Detection**: Automatically recognize exercise from pose
- **Form Analysis**: Rule-based mistake detection with severity levels
- **Instant Corrections**: Specific, actionable feedback
- **Fatigue Monitoring**: Real-time fatigue detection (7 indicators)
- **AI Coaching**: On-demand Gemini AI expert feedback
- **Clean Mobile UI**: Native iOS app with Expo

### 🔄 In Progress

- Testing end-to-end flow
- Performance optimization

### 📋 Future Enhancements

- On-device ML (no backend needed)
- Offline mode
- Workout history & stats
- Rep counting
- Multi-angle support
- Android support
- Social features

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MediaPipe**: Google's ML pose detection
- **OpenCV**: Image processing
- **TensorFlow**: ML backend
- **Google Gemini**: Advanced AI coaching

### Mobile
- **React Native**: Cross-platform mobile framework
- **Expo**: Development and build tooling
- **TypeScript**: Type safety
- **expo-camera**: Camera access
- **Axios**: HTTP client

## API Endpoints

### `GET /health`
Health check and model status

### `GET /api/exercises`
List supported exercises

### `POST /api/analyze`
Analyze posture from image
- **Input**: `{ image: base64, exercise?: string }`
- **Output**: Exercise, mistakes, angles, fatigue

### `POST /api/gemini-feedback`
Get AI coaching feedback
- **Input**: `{ image: base64, exercise, angles, mistakes }`
- **Output**: Detailed AI analysis

## Configuration

### Backend Performance

Edit `api/main.py`:
```python
# Adjust MediaPipe confidence thresholds
min_pose_detection_confidence = 0.5
min_tracking_confidence = 0.5
```

### Mobile Performance

Edit `mobile/src/screens/WorkoutSession.tsx`:
```typescript
// Adjust frame rate (lower = less API calls)
const throttlerRef = useRef(new FrameThrottler(2)); // 2 FPS

// Adjust image quality
const frameBase64 = await captureFrame(cameraRef, 0.6); // 60%
```

## Development Workflow

### Working on Backend

```bash
# Run with auto-reload
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/exercises
```

### Working on Mobile

```bash
cd mobile
npm start -- --clear  # Clear cache if needed
```

Changes auto-reload in Expo Go.

## Testing

### Test Backend Directly

```bash
# Health check
curl http://localhost:8000/health

# Analyze with test image
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_string"}'
```

### Test Mobile App

1. Start backend
2. Update API URL in mobile app
3. Run on iOS simulator
4. Perform exercises in front of camera
5. Verify real-time feedback

## Troubleshooting

### Backend Issues

**Models not loading:**
- Check MediaPipe installation: `pip list | grep mediapipe`
- Download pose model manually if needed

**Import errors:**
- Ensure you're in project root
- Check `sys.path` in api/main.py

### Mobile Issues

**Backend unreachable:**
- Verify backend is running: `curl http://localhost:8000/health`
- Check API URL matches backend IP
- Ensure same WiFi network (physical device)

**Camera not working:**
- Check permissions in iOS Settings
- Verify expo-camera installation
- Try restarting Expo

**Slow performance:**
- Reduce FPS (1-2 for POC)
- Lower image quality (0.5)
- Use iOS simulator instead of Expo Go

## Branch Information

This POC is on the `react-native-poc` branch, created from `vincksi-patch` (the most advanced posture analysis implementation).

### Other Branches

- `main`: Initial commit
- `vincksi-patch`: Advanced posture analyzer (base for this POC)
- `arthur`: Backend with FastAPI + Firebase
- `yiwen`: Gemini ADK agent
- `ai-team`: Basic posture analysis

## Contributing

When making changes:

1. Test backend independently first
2. Test mobile app with backend running
3. Verify end-to-end flow
4. Update relevant README files
5. Commit your changes (tool won't auto-commit)

## Known Limitations

- **Backend Required**: App needs server running (not on-device ML)
- **iOS Only**: Android not configured yet (easy to add)
- **No Persistence**: No workout history/database
- **Network Dependent**: Requires connectivity for analysis
- **Privacy**: Frames sent to backend (not end-to-end encrypted)
- **Battery**: Continuous camera + API calls drain battery

## Performance Notes

- **Frame Rate**: 2 FPS recommended for POC (responsive + low load)
- **Image Quality**: 60% JPEG (good quality + small size)
- **API Latency**: ~200-500ms per analysis (depends on network)
- **Gemini Calls**: On-demand only (expensive, ~1-2s latency)

## License

See project LICENSE file

## Support

- Backend API docs: `api/README.md`
- Mobile app docs: `mobile/README.md`
- Posture analyzer: Original `README.md` from vincksi-patch branch
