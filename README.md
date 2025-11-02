# AI Sport Coach

Real-time posture analysis for workout exercises using MediaPipe and Gemini AI. Mobile app provides live form correction feedback through camera-based pose detection.

## Tech Stack

**Backend:** Python, FastAPI, MediaPipe, Gemini AI
**Mobile:** React Native (Expo), TypeScript
**Package Management:** UV for Python, npm for mobile

## Setup

### Backend

1. Install Python dependencies:
```bash
uv sync
```

2. Download MediaPipe model:
```bash
curl -o pose_landmarker_lite.task https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task
```

3. (Optional) Set Gemini API key in `.env`:
```bash
GEMINI_API_KEY=your_key_here
```

4. Start backend with ngrok:
```bash
uv run python start_backend_ngrok.py
```

Copy the ngrok URL from the output.

### Mobile App

1. Install dependencies:
```bash
cd mobile
npm install
```

2. Configure backend URL in `mobile/.env`:
```
EXPO_PUBLIC_API_URL=https://your-ngrok-url.ngrok-free.app
```

3. Start Expo:
```bash
npm start
```

4. Scan QR code with Expo Go app (iOS/Android)

## Usage

1. Grant camera permissions when prompted
2. Select exercise type or use auto-detect
3. Tap "Start Analysis" to begin
4. View real-time feedback overlay with skeleton visualization
5. Tap "AI Feedback" for detailed coaching from Gemini

## Supported Exercises

- Squats
- Push-ups
- Planks
- Deadlifts
- Lunges

## Project Structure

```
├── api/                    # FastAPI backend
├── posture_analyzer/       # Pose detection & analysis logic
├── mobile/                 # React Native app
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── screens/        # Main workout screen
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript definitions
├── start_backend_ngrok.py  # Backend startup script
└── pyproject.toml          # Python dependencies
```
