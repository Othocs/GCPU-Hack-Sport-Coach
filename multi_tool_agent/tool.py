import asyncio
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

APP_NAME="weather_sentiment_agent"
USER_ID="user1234"
SESSION_ID="1234"
MODEL_ID="gemini-2.0-flash"

# Tool 1: Mediapipe pose estimation
def estimate_pose(image: bytes) -> str:
    """
    Runs Mediapipe inference for pose landmarking.
    Returns: a list of landmarks
    """
    return 