from __future__ import annotations

import contextlib
import io
import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import calendar_call
import eating_call
import main as firebase_main


logger = logging.getLogger("main_fastapi")


class CalendarRequest(BaseModel):
    weeks: int = 4
    uid: str | None = None


class MealRequest(BaseModel):
    weeks: int = 1
    include_shopping_list: bool = False
    uid: str | None = None


app = FastAPI(
    title="Sports Planner API",
    version="1.0.0",
    description="Endpoints that expose the training calendar, meal planner, and Firebase smoke test.",
)


@app.get("/health", tags=["meta"])
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/calendar", tags=["calendar"])
def generate_calendar(request: CalendarRequest) -> Dict[str, Any]:
    try:
        return calendar_call.build_training_calendar(request.weeks, request.uid)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/meals", tags=["nutrition"])
def generate_meals(request: MealRequest) -> Dict[str, Any]:
    try:
        meal_plan = eating_call.build_meal_plan(request.weeks, request.uid)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    response: Dict[str, Any] = {"meal_plan": meal_plan}
    if request.include_shopping_list:
        response["shopping_list"] = eating_call.generate_shopping_list(meal_plan)
    return response


@app.post("/firebase/test", tags=["firebase"])
def firebase_test() -> Dict[str, Any]:
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            firebase_main.main()
    except Exception as exc:  # pragma: no cover - network and external service dependent
        logger.exception("Firebase diagnostics failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"output": buffer.getvalue()}


# Optional root convenience
@app.get("/", tags=["meta"])
def root() -> Dict[str, str]:
    return {
        "message": "Sports Planner API is running",
        "docs": "/docs",
        "calendar_endpoint": "/calendar",
        "meals_endpoint": "/meals",
        "firebase_endpoint": "/firebase/test",
    }
