from __future__ import annotations

import argparse
import json
from collections import deque
from typing import Any, Dict, Iterable, List

import data_call

def select_allowed_exercises(exercises: Iterable[Dict[str, Any]], experience_level: str) -> List[Dict[str, Any]]:
    level = experience_level.lower()

    def is_suitable(item: Dict[str, Any]) -> bool:
        difficulty = item.get("difficulty", "beginner").lower()
        if level == "beginner":
            return difficulty in {"beginner", "easy"}
        if level in {"intermediate", "moderate"}:
            return difficulty in {"beginner", "intermediate", "moderate"}
        return True

    filtered = [item for item in exercises if is_suitable(item)]
    if not filtered:
        raise ValueError("No exercises available after filtering by experience level.")
    return filtered


def determine_sets_reps(intensity: str, experience_level: str) -> Dict[str, int]:
    level = experience_level.lower()
    intensity_level = intensity.lower()

    sets = 3
    reps = 12
    rest = 60

    if intensity_level in {"low", "light"}:
        reps = 15
        rest = 45
    elif intensity_level in {"high", "vigorous"}:
        sets = 4
        reps = 10
        rest = 75

    if level in {"beginner", "novice"}:
        reps = min(reps, 12)
        rest = max(rest, 60)
    elif level in {"intermediate", "moderate"}:
        sets = max(sets, 3)
    else:  # advanced
        sets = max(sets, 4)
        reps = min(reps, 10)

    return {"sets": sets, "repetitions": reps, "rest_seconds": rest}


def session_exercises(
    rotation: deque,
    num_exercises: int,
    sets: int,
    reps: int,
    rest_seconds: int,
) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []
    count = max(1, min(num_exercises, len(rotation)))

    for index in range(count):
        current = rotation[0]
        rotation.rotate(-1)
        blocks.append(
            {
                "id": current.get("id"),
                "name": current.get("name"),
                "sets": sets,
                "repetitions": reps,
                "rest_seconds": rest_seconds,
                "notes": "Maintain controlled tempo and prioritize technique.",
            }
        )
        if index < count - 1:
            blocks.append(
                {
                    "type": "break",
                    "duration_seconds": rest_seconds,
                    "notes": "Light mobility work and hydration.",
                }
            )

    # Conclude every session with a cooldown break
    blocks.append(
        {
            "type": "break",
            "duration_seconds": rest_seconds,
            "notes": "Deep breathing and stretching cooldown.",
        }
    )
    return blocks


def build_training_calendar(weeks: int, uid: str | None = None) -> Dict[str, Any]:
    if weeks <= 0:
        raise ValueError("Number of weeks must be a positive integer.")

    user_id = uid or data_call.DEFAULT_USER_ID
    user = data_call.get_user_profile(user_id)
    allowed_exercises = data_call.get_allowed_exercises()
    chatbot_config = data_call.get_chatbot_config()

    exercises = select_allowed_exercises(allowed_exercises["exercises"], user.get("experience_level", "beginner"))

    # simple rotation to distribute exercises across sessions
    rotation = deque(sorted(exercises, key=lambda item: item["name"]))

    training_days = user.get("training_days") or []
    if not training_days:
        raise ValueError("User profile does not define any training days.")

    training_sessions: List[Dict[str, Any]] = []
    parameters = determine_sets_reps(user.get("training_intensity", "moderate"), user.get("experience_level", "beginner"))
    num_exercises_per_session = 3 if len(exercises) >= 3 else len(exercises)

    for week_index in range(1, weeks + 1):
        week_sessions = []
        for day in training_days:
            session = {
                "week": week_index,
                "day": day,
                "duration": user.get("training_time", "1 hour"),
                "intensity": user.get("training_intensity", "moderate"),
                "exercises": session_exercises(
                    rotation,
                    num_exercises_per_session,
                    parameters["sets"],
                    parameters["repetitions"],
                    parameters["rest_seconds"],
                ),
            }
            week_sessions.append(session)
        training_sessions.append({"week": week_index, "sessions": week_sessions})

    output = {
        "user_id": user.get("id"),
        "user_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
        "project_id": chatbot_config.get("project_id") or chatbot_config.get("projectId") or data_call.get_chatbot_project_id(),
        "weeks": training_sessions,
    }
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a training calendar for the simulated user.")
    parser.add_argument("weeks", type=int, nargs="?", default=4, help="Number of weeks to generate (default: 4)")
    parser.add_argument("--uid", default=data_call.DEFAULT_USER_ID, help="User ID to build the calendar for")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    calendar = build_training_calendar(args.weeks, args.uid)
    print(json.dumps(calendar, indent=2))


if __name__ == "__main__":
    main()
