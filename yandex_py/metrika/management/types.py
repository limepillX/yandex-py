from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CounterGoal(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    type: str | None = None
    status: str | None = None


class MetrikaCounter(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int
    name: str | None = None
    goals: list[CounterGoal] = []


class CounterGoalsResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    rows: int | None = None
    counters: list[MetrikaCounter]
