# AI Sport Coach - React Native Mobile App

React Native mobile app for real-time posture correction using AI-powered analysis.

## Features

- **Real-time Posture Analysis**: Live camera feed with posture detection
- **Exercise Recognition**: Auto-detect or manually select exercises (squat, pushup, plank, deadlift, lunge)
- **Form Corrections**: Instant feedback on mistakes with severity levels
- **AI Coaching**: On-demand detailed feedback from Google Gemini AI
- **Fatigue Monitoring**: Real-time fatigue detection and warnings

## Prerequisites

- Node.js 18+ and npm
- iOS Simulator (macOS with Xcode) or physical iOS device
- Python 3.9+ with UV package manager
- Backend API running (see `../api/README.md`)

## Setup

### 1. Install Dependencies

```bash
cd mobile
npm install
```

### 2. Configure Backend URL

The app connects to the backend API via environment variables.

**Option A: Using Ngrok (Recommended)**

This works from anywhere - no need for same WiFi or local IP!

```bash
# Create .env file from template
cp .env.example .env

# The .env file will look like this (don't edit yet):
# EXPO_PUBLIC_API_URL=https://your-ngrok-url.ngrok.io
```

When you start the backend with ngrok (step 3), you'll get a URL to copy here.

**Option B: Local Network (Alternative)**

For physical iOS device on same WiFi:
```bash
# In .env file, use your computer's local IP
EXPO_PUBLIC_API_URL=http://192.168.1.100:8000
```
Find your IP: `ifconfig | grep "inet " | grep -v 127.0.0.1`

For iOS Simulator:
```bash
# In .env file, use localhost
EXPO_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start the Backend API

In a separate terminal, start the backend:

**Option A: With Ngrok (Recommended)**

```bash
# From project root
uv sync  # First time only - install dependencies
uv run python start_backend_ngrok.py
```

You'll see output like:
```
======================================================================
🚀 AI Sport Coach Backend Started!
======================================================================

✓ Local backend:  http://localhost:8000
✓ Public URL:     https://abc123.ngrok.io

📱 For mobile app, copy this to mobile/.env:

   EXPO_PUBLIC_API_URL=https://abc123.ngrok.io

======================================================================
```

**Copy the URL** and paste it in your `mobile/.env` file!

**Option B: Without Ngrok (Local Only)**

```bash
# From project root
uv run python api/main.py
```

Verify it's running:
```bash
curl http://localhost:8000/health
```

### 4. Run the App

Start Expo:

```bash
npm start
```

Then press:
- `i` for iOS Simulator
- Scan QR code with Expo Go app on physical device

## Usage

### Basic Workflow

1. **Grant Camera Permission**: On first launch, allow camera access
2. **Select Exercise**: Choose auto-detect or specific exercise type
3. **Start Analysis**: Tap "Start Analysis" button
4. **Get Feedback**: View real-time corrections on screen
5. **AI Coaching**: Tap "AI Feedback" for detailed Gemini analysis

### Exercise Selection

- **Auto-Detect**: App automatically recognizes exercise (recommended)
- **Manual Selection**: Choose specific exercise for more accurate analysis
  - Squat
  - Push-up
  - Plank
  - Deadlift
  - Lunge

### Understanding Feedback

**Severity Levels:**
- 🔴 **Red (Severe)**: Safety-critical issues, fix immediately
- 🟡 **Yellow (Moderate)**: Performance issues, should improve
- 🟢 **Green (Good)**: Excellent form!

**Fatigue Warning:**
- Appears when overall fatigue score > 30%
- Suggests taking a rest to prevent injury

## Project Structure

```
mobile/
├── src/
│   ├── screens/
│   │   └── WorkoutSession.tsx      # Main workout screen
│   ├── components/
│   │   ├── FeedbackOverlay.tsx     # Analysis results overlay
│   │   └── ExerciseSelector.tsx    # Exercise type selector
│   ├── services/
│   │   └── apiClient.ts            # Backend API client
│   ├── types/
│   │   └── analysis.ts             # TypeScript interfaces
│   └── utils/
│       └── frameCapture.ts         # Camera frame utilities
├── App.tsx                         # Root component
├── app.json                        # Expo configuration
└── package.json
```

## Configuration

### Frame Rate

Adjust analysis frequency in `WorkoutSession.tsx`:

```typescript
const throttlerRef = useRef(new FrameThrottler(2)); // 2 FPS (default)
```

Higher FPS = more responsive but more backend calls and battery usage.

### Image Quality

Modify JPEG quality in frame capture:

```typescript
const frameBase64 = await captureFrame(cameraRef, 0.6); // 60% quality
```

Lower quality = faster upload but less accurate analysis.

## Troubleshooting

### "Backend Unreachable" Error

**If using ngrok:**
1. Verify backend + ngrok is running: `uv run python start_backend_ngrok.py`
2. Check the ngrok URL in `mobile/.env` matches what was printed
3. Make sure the URL starts with `https://` (not `http://`)
4. Ngrok free tier sessions last ~2 hours - restart if expired

**If using local network:**
1. Verify backend is running: `curl http://YOUR_IP:8000/health`
2. Check API URL in `mobile/.env` matches backend IP
3. Ensure firewall allows port 8000
4. For physical device: both device and computer must be on same network

### Camera Not Working

1. Check camera permissions in iOS Settings
2. Verify `expo-camera` is installed: `npm list expo-camera`
3. Try restarting Expo: `npm start -- --clear`

### Slow Performance

1. Reduce frame rate (lower FPS in FrameThrottler)
2. Lower image quality (0.5 instead of 0.7)
3. Use iOS Simulator instead of Expo Go for testing

### "No Pose Detected"

1. Ensure good lighting
2. Stand 3-6 feet from camera
3. Keep full body in frame
4. Try different exercise or manual selection

## Development

### Run with Development Build

For better performance than Expo Go:

```bash
# Create development build
npx expo run:ios

# Or for Android
npx expo run:android
```

### Enable Hot Reload

Changes to source files will auto-reload. For major changes:

```bash
npm start -- --clear
```

## Building for Production

### iOS

1. Configure bundle identifier in `app.json`
2. Set up Apple Developer account
3. Build:

```bash
eas build --platform ios
```

### Android

```bash
eas build --platform android
```

See [Expo EAS Build docs](https://docs.expo.dev/build/introduction/) for details.

## Known Limitations (POC)

- Backend must be running and reachable
- No offline mode
- No workout history/persistence
- iOS only (Android support can be added)
- Requires internet for Gemini AI feedback
- Frame processing is server-side (privacy consideration)

## Future Enhancements

- On-device ML processing (MediaPipe mobile SDK)
- Offline mode with cached feedback
- Workout history and progress tracking
- Multiple camera angles
- Rep counting
- Social features / workout sharing
- Apple Health integration

## License

See parent project LICENSE
