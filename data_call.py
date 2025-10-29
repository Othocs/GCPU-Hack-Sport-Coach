from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable
from urllib import error, parse, request


LOGGER = logging.getLogger("data_call")

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
SIM_DATA_DIR = BASE_DIR / "simulated_data"

FIREBASE_CONFIG_PATH = CONFIG_DIR / "firebase.json"
SIM_USER_PROFILE_PATH = SIM_DATA_DIR / "user1.json"
SIM_WORKOUT_PLAN_PATH = SIM_DATA_DIR / "user1_workoutPlan.json"
SIM_ALLOWED_EXERCISES_PATH = SIM_DATA_DIR / "allowed_exercises.json"
CHATBOT_CONFIG_PATH = CONFIG_DIR / "chatBot.json"

DEFAULT_USER_ID = "1234567890"


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_optional_json(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return _load_json(path)
    except json.JSONDecodeError as exc:  # pragma: no cover - data error defensive
        LOGGER.warning("Failed to parse JSON at %s: %s", path, exc)
        return None


def _firebase_config() -> Dict[str, str] | None:
    data = _load_optional_json(FIREBASE_CONFIG_PATH)
    if not data:
        return None
    project_id = data.get("projectId") or data.get("project_id")
    api_key = data.get("apiKey") or data.get("api_key")
    if not project_id or not api_key:
        LOGGER.warning("Firebase config missing project_id/apiKey")
        return None
    return {"project_id": project_id, "api_key": api_key}


FIREBASE_SETTINGS = _firebase_config()


def _firestore_base_url() -> str | None:
    if not FIREBASE_SETTINGS:
        return None
    return (
        f"https://firestore.googleapis.com/v1/projects/{FIREBASE_SETTINGS['project_id']}"
        "/databases/(default)"
    )


def _call_firestore(
    method: str,
    endpoint: str,
    params: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if not FIREBASE_SETTINGS:
        raise RuntimeError("Firebase configuration unavailable")

    base_url = _firestore_base_url()
    if not base_url:
        raise RuntimeError("Firebase base URL unavailable")

    request_params = dict(params or {})
    request_params.setdefault("key", FIREBASE_SETTINGS["api_key"])
    query = parse.urlencode(request_params, doseq=True)
    url = f"{base_url}/{endpoint.lstrip('/') }"
    if query:
        url = f"{url}?{query}"

    req = request.Request(url, method=method.upper())

    try:
        with request.urlopen(req) as response:
            if response.status == 204:
                return {}
            return json.load(response)
    except error.HTTPError as exc:
        payload: Dict[str, Any] | None = None
        try:
            payload = json.loads(exc.read())
        except json.JSONDecodeError:
            payload = None
        message = payload.get("error", {}).get("message") if payload else exc.reason
        raise RuntimeError(f"Firestore request failed: {message}") from exc


def _decode_value(value: Dict[str, Any]) -> Any:
    if "nullValue" in value:
        return None
    if "booleanValue" in value:
        return value["booleanValue"]
    if "integerValue" in value:
        return int(value["integerValue"])
    if "doubleValue" in value:
        return value["doubleValue"]
    if "stringValue" in value:
        return value["stringValue"]
    if "timestampValue" in value:
        return value["timestampValue"]
    if "arrayValue" in value:
        return [_decode_value(item) for item in value["arrayValue"].get("values", [])]
    if "mapValue" in value:
        fields = value["mapValue"].get("fields", {})
        return {key: _decode_value(inner) for key, inner in fields.items()}
    return value


def _decode_document(document: Dict[str, Any]) -> Dict[str, Any]:
    fields = document.get("fields", {})
    result = {key: _decode_value(value) for key, value in fields.items()}
    if "name" in document:
        result["_firestore_name"] = document["name"]
    return result


def _firestore_get(path: str) -> Dict[str, Any] | None:
    if not FIREBASE_SETTINGS:
        return None
    try:
        document = _call_firestore("GET", path)
    except RuntimeError as exc:
        LOGGER.info("Firestore lookup failed for %s: %s", path, exc)
        return None
    if not document:
        return None
    if "documents" in document:
        return {"documents": [_decode_document(doc) for doc in document["documents"]]}
    return _decode_document(document)


def get_user_profile(uid: str = DEFAULT_USER_ID) -> Dict[str, Any]:
    path = f"documents/users/{uid}"
    document = _firestore_get(path)
    if document:
        return document
    fallback = _load_optional_json(SIM_USER_PROFILE_PATH)
    if fallback:
        return fallback
    raise FileNotFoundError(f"User profile for {uid} not found in Firestore or local data")


def get_user_habits(uid: str = DEFAULT_USER_ID) -> Iterable[Dict[str, Any]]:
    profile = get_user_profile(uid)
    return profile.get("habits", [])


def get_user_workout_plan(uid: str = DEFAULT_USER_ID) -> Dict[str, Any]:
    path = f"documents/workoutPlans/{uid}"
    document = _firestore_get(path)
    if document:
        return document
    fallback = _load_optional_json(SIM_WORKOUT_PLAN_PATH)
    if fallback:
        return fallback
    raise FileNotFoundError(f"Workout plan for {uid} not found in Firestore or local data")


def get_allowed_exercises() -> Dict[str, Any]:
    path = "documents/metadata/allowed_exercises"
    document = _firestore_get(path)
    if document and "exercises" in document:
        return document
    fallback = _load_optional_json(SIM_ALLOWED_EXERCISES_PATH)
    if fallback:
        return fallback
    raise FileNotFoundError("Allowed exercises data not available")


def get_chatbot_config() -> Dict[str, Any]:
    data = _load_optional_json(CHATBOT_CONFIG_PATH)
    return data or {}


def get_chatbot_project_id() -> str | None:
    config = get_chatbot_config()
    return config.get("project_id") or config.get("projectId")

