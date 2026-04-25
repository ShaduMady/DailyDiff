from datetime import datetime
from pydantic import BaseModel


class EntryCreate(BaseModel):
    raw_text: str


class EntryResponse(BaseModel):
    id: int
    version: str
    raw_text: str
    summary: str
    tags: list[str]
    changelog: list[str]
    key_ideas: list[str]
    open_questions: list[str]
    action_items: list[str]
    drift_score: int
    connections: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WeeklySummaryResponse(BaseModel):
    week_version: str
    summary: str
    highlights: list[str]
    blockers: list[str]
    pattern: str


class SettingUpdate(BaseModel):
    value: str


class SettingResponse(BaseModel):
    value: str
