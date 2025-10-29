## GCPU Hack Sport Coach — Project Overview

A lightweight project that organizes logic for a sports coaching assistant. It includes simple modules for data access, nutrition/eating guidance, and calendar scheduling, plus a FastAPI entry point for exposing APIs.

### Repository structure

```
GCPU-Hack-Sport-Coach/
├─ calendar_call.py           # Calendar utilities (e.g., schedule workouts/meals)
├─ data_call.py               # Data access/helpers for users, plans, and datasets
├─ eating_call.py             # Nutrition/eating guidance utilities
├─ main_fastapi.py            # FastAPI application entry point (API server)
├─ main.py                    # Script/runner entry point (local runs or demos)
├─ config/
│  ├─ chatBot.json            # Chatbot/system configuration and prompts
│  └─ firebase.json           # Firebase-related configuration
├─ simulated_data/
│  ├─ allowed_exercises.json  # Example catalog of allowed exercises
│  ├─ user1.json              # Example user profile data
│  └─ user1_workoutPlan.json  # Example user workout plan
├─ requirements.txt           # Python dependencies
├─ pyproject.toml             # Project metadata and tooling configuration
└─ README.md                  # This file
```

### What each part does (brief)

- **calendar_call.py**: Functions to create/find/update calendar events tied to workouts and meals.
- **data_call.py**: Helpers for loading and manipulating user data and workout plans (uses files in `simulated_data/`).
- **eating_call.py**: Logic/utilities for simple nutrition or eating plan suggestions.
- **main_fastapi.py**: Defines the FastAPI app to expose the coaching features over HTTP.
- **main.py**: Local script entry point for quick tests or CLI-style runs.
- **config/**: JSON configs used by the app (chatbot prompts/toggles, Firebase settings, etc.).
- **simulated_data/**: Small sample datasets to run the app without external services.
- **requirements.txt / pyproject.toml**: Dependency pins and project config for Python tooling.

### Quick notes

- The code assumes local files in `simulated_data/` for demo data; replace or wire to real backends as needed.
- Keep sensitive keys out of version control; treat `config/firebase.json` as example-only.

