# Ngrok Setup Guide

Quick guide for using ngrok to connect your mobile app to the backend from anywhere.

## Why Ngrok?

✅ **Works from anywhere** - WiFi, cellular data, different networks
✅ **No IP configuration** - One stable HTTPS URL
✅ **No firewall issues** - Bypasses network restrictions
✅ **Easy sharing** - Share URL with teammates
✅ **Free tier** - No payment required for basic use

## Setup (5 minutes)

### Step 1: Install Dependencies

```bash
# From project root
cd /path/to/GCPU-Hack-Sport-Coach
uv sync
```

This installs `pyngrok` along with all other dependencies.

### Step 2: Start Backend with Ngrok

```bash
uv run python start_backend_ngrok.py
```

You'll see:

```
======================================================================
🚀 AI Sport Coach Backend Started!
======================================================================

✓ Local backend:  http://localhost:8000
✓ Public URL:     https://abc123-xyz789.ngrok.io

📱 For mobile app, copy this to mobile/.env:

   EXPO_PUBLIC_API_URL=https://abc123-xyz789.ngrok.io

======================================================================
💡 Tip: The URL is valid until you stop this script
Press Ctrl+C to stop the server
======================================================================
```

**Copy the URL** (the `https://abc123-xyz789.ngrok.io` part)

### Step 3: Configure Mobile App

```bash
cd mobile

# Create .env file if you haven't already
cp .env.example .env

# Edit .env and paste your ngrok URL
nano .env
```

Your `.env` should look like:
```
EXPO_PUBLIC_API_URL=https://abc123-xyz789.ngrok.io
```

### Step 4: Start Mobile App

```bash
npm start

# Then press 'i' for iOS simulator
# Or scan QR code with Expo Go on your phone
```

### Step 5: Test!

1. Grant camera permission
2. Select an exercise or use auto-detect
3. Tap "Start Analysis"
4. Perform your exercise
5. See real-time feedback!

## Important Notes

### Ngrok Free Tier Limits

- **Session duration**: ~2 hours per tunnel
- **Reconnection**: When it expires, restart and get new URL
- **URL changes**: Each restart gives a new URL - update `.env`
- **Concurrent tunnels**: 1 tunnel at a time on free tier

### When URL Expires

If you see "Backend Unreachable" after ~2 hours:

```bash
# Terminal 1: Restart backend (get new URL)
Ctrl+C  # Stop the old server
uv run python start_backend_ngrok.py  # Start new one

# Terminal 2: Update mobile .env with new URL
cd mobile
nano .env  # Paste the new ngrok URL

# Restart Expo to pick up new URL
npm start
```

### Security Notes

- **Public URL**: Anyone with your ngrok URL can access your backend
- **Development only**: Don't use for production
- **Local data**: All processing happens on your computer, frames just pass through ngrok
- **Temporary**: URLs expire when you stop the server

## Troubleshooting

### "Failed to create ngrok tunnel"

**Solution 1: Check internet connection**
```bash
ping google.com
```

**Solution 2: Kill existing ngrok processes**
```bash
pkill ngrok
uv run python start_backend_ngrok.py
```

**Solution 3: Check ngrok installation**
```bash
uv run python -c "import pyngrok; print('OK')"
```

### Mobile app can't connect

1. **Check URL format**: Must be `https://`, not `http://`
2. **Restart Expo**: After changing `.env`, restart with `npm start`
3. **Verify backend is running**: Check terminal shows ngrok URL
4. **Test URL**: Open ngrok URL in browser, should see backend response

### URL expired

Normal behavior! Free tier sessions last ~2 hours. Just:
1. Restart backend
2. Copy new URL
3. Update mobile `.env`
4. Restart Expo

## Alternative: Local Network (No Ngrok)

If you don't want to use ngrok, use local network:

```bash
# Terminal 1: Start backend normally
uv run python api/main.py

# Terminal 2: Find your computer's IP
ifconfig | grep "inet " | grep -v 127.0.0.1
# Example output: inet 192.168.1.100

# Terminal 3: Configure mobile app
cd mobile
echo "EXPO_PUBLIC_API_URL=http://192.168.1.100:8000" > .env
npm start
```

**Requirements:**
- Phone and computer on same WiFi
- Firewall allows port 8000
- IP address can change when switching networks

## Quick Reference

| Scenario | Command | Notes |
|----------|---------|-------|
| First time setup | `uv sync` | Install dependencies |
| Start with ngrok | `uv run python start_backend_ngrok.py` | Get public URL |
| Start without ngrok | `uv run python api/main.py` | Local only |
| Stop server | `Ctrl+C` | In backend terminal |
| Update mobile URL | Edit `mobile/.env` | Restart Expo after |
| Check backend health | `curl <your-url>/health` | Should return JSON |

## Benefits Summary

**Ngrok approach:**
- ✅ Works from anywhere
- ✅ Cellular data supported
- ✅ Easy for teammates
- ⚠️ URL expires after 2 hours
- ⚠️ Publicly accessible

**Local network approach:**
- ✅ No URL expiration
- ✅ Fully private
- ✅ No external dependencies
- ⚠️ Same WiFi required
- ⚠️ IP configuration needed

Choose based on your needs!
