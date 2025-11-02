#!/usr/bin/env python3
"""Start FastAPI backend with ngrok tunnel"""

import sys
import os
import threading
import time
from pyngrok import ngrok

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def print_banner(ngrok_url):
    """Print startup information with ngrok URL"""
    print("\n" + "=" * 70)
    print("🚀 AI Sport Coach Backend Started!")
    print("=" * 70)
    print(f"\n✓ Local backend:  http://localhost:8000")
    print(f"✓ Public URL:     {ngrok_url}")
    print(f"\n📱 For mobile app, copy this to mobile/.env:")
    print(f"\n   EXPO_PUBLIC_API_URL={ngrok_url}")
    print(f"\n{'=' * 70}")
    print("💡 Tip: The URL is valid until you stop this script")
    print("Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")


def start_ngrok_tunnel(port=8000):
    """Start ngrok tunnel and return public URL"""
    try:
        ngrok.kill()
        print("🔧 Creating ngrok tunnel...")
        public_url = ngrok.connect(port, bind_tls=True)
        return public_url.public_url
    except Exception as e:
        print(f"❌ Failed to create ngrok tunnel: {e}")
        print("\n💡 Tips:")
        print("  1. Make sure you have internet connection")
        print("  2. Ngrok free tier may have limits (2 hours session)")
        print("  3. Check if another ngrok is running: pkill ngrok")
        sys.exit(1)


def run_backend():
    """Run the FastAPI backend"""
    import uvicorn
    from api.main import app

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=False,
    )
    server = uvicorn.Server(config)
    server.run()


def main():
    """Main entry point"""
    print("\n🔧 Starting AI Sport Coach Backend with Ngrok...")
    print("⏳ This may take a few seconds...\n")

    ngrok_url = start_ngrok_tunnel(port=8000)
    print_banner(ngrok_url)

    try:
        run_backend()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        ngrok.kill()
        print("✓ Ngrok tunnel closed")
        print("✓ Backend stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
