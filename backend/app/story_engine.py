"""Placeholder for Member 4's story_engine module."""
from .schemas import Article, Ending, Scene, StoryStep


async def generate_scene(article: Article, steps: list[StoryStep], turn: int) -> Scene:
    raise NotImplementedError("Provided by Member 4")


async def generate_ending(article: Article, steps: list[StoryStep]) -> Ending:
    raise NotImplementedError("Provided by Member 4")
