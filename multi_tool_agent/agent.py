from google.adk.agents.llm_agent import Agent
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types


root_agent = Agent(
    model='gemini-2.5-flash', # supports live, but not thinking
    name='root_agent',
    description='A helpful assistant to judge the accuracy of yoga posture.',
    instruction="Answer user questions to the best of your knowledge.If the last answer from you is suggestions of user's poseture, you google search suitable videos to correct her specific posture",
    tools=[google_search]
)
