"""Shared schema definitions for Gemma Story Engine.

Complies with the team contract (Member 3 backend contract):
- JSON serialization uses camelCase
- Python code uses snake_case
"""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

TOTAL_TURNS = 5
ChoiceId = Literal["A", "B", "C"]


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class Article(CamelModel):
    title: str
    extract: str
    url: str
    thumbnail_url: str | None = None


class Choice(CamelModel):
    id: ChoiceId
    text: str


class Scene(CamelModel):
    turn: int
    narrative: str
    choices: list[Choice]
    fact: str


class Ending(CamelModel):
    title: str
    narrative: str
    lesson: str


class StoryStep(CamelModel):
    """Context of a completed turn: scene shown and player's chosen branch."""
    turn: int
    narrative: str
    choices: list[Choice]
    chosen_id: ChoiceId
    chosen_text: str


class GenerateSceneRequest(CamelModel):
    article: Article
    steps: list[StoryStep] = Field(default_factory=list)
    turn: int = Field(default=1, ge=1, le=TOTAL_TURNS)


class GenerateEndingRequest(CamelModel):
    article: Article
    steps: list[StoryStep] = Field(min_length=1)


class HealthResponse(CamelModel):
    status: str
    model: str
    mock_mode: bool
    api_key_configured: bool
