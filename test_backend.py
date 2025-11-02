"""
Quick test script for the FastAPI backend
Tests basic endpoints without requiring camera/images
"""

import requests
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to backend. Is it running?")
        print("  Start with: cd api && python main.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_exercises():
    """Test exercises endpoint"""
    print("\nTesting /api/exercises endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/exercises", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Got exercises: {data['exercises']}")
            return True
        else:
            print(f"✗ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("=== Backend API Test ===\n")

    # Test health
    health_ok = test_health()
    if not health_ok:
        print("\n❌ Backend is not running or not accessible")
        print("Please start the backend first:")
        print("  uv sync  # Install dependencies if not done yet")
        print("  uv run python api/main.py")
        sys.exit(1)

    # Test exercises
    exercises_ok = test_exercises()

    if health_ok and exercises_ok:
        print("\n✅ All tests passed! Backend is ready.")
        print("\nNext steps:")
        print("1. Configure your Gemini API key in .env file")
        print("2. Start the mobile app: cd mobile && npm start")
        print("3. Update API URL in mobile/src/services/apiClient.ts")
    else:
        print("\n⚠ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
