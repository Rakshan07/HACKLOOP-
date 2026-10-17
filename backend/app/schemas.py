"""Shared data shapes (the contract). Owner: Member 3. Frozen: change only with the whole team.

JSON sent to the browser uses camelCase (gameId, choiceId...). Python code uses snake_case.
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


class HistoryItem(CamelModel):
    turn: int
    choice_id: ChoiceId
    choice_text: str


class GameView(CamelModel):
    game_id: str
    status: Literal["ARTICLE_READY", "PLAYING", "COMPLETED"]
    turn: int
    total_turns: int = TOTAL_TURNS
    article: Article
    scene: Scene | None = None
    ending: Ending | None = None
    history: list[HistoryItem] = []


class ChoiceRequest(CamelModel):
    model_config = ConfigDict(extra="forbid")  # unknown fields are rejected
    turn: int = Field(ge=1, le=TOTAL_TURNS)
    choice_id: ChoiceId


class StoryStep(CamelModel):
    """One finished turn: the scene the player saw and what they picked. Used as AI context."""
    turn: int
    narrative: str
    choices: list[Choice]
    chosen_id: ChoiceId
    chosen_text: str
