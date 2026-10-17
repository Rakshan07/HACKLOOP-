"""Gemma Story Engine bridge. Owner: Member 4 integration.

Connects Member 3's game_service to the Gemma AI Story Engine.
"""
import sys
from pathlib import Path

# Add repository root to python path to access gemma_service
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from gemma_service import engine as gemma_engine
from .schemas import Article, Ending, Scene, StoryStep


async def generate_scene(article: Article, steps: list[StoryStep], turn: int) -> Scene:
    # Convert schemas to gemma_service types (identical structure)
    scene = await gemma_engine.generate_scene(article, steps, turn)
    return Scene.model_validate(scene.model_dump())


async def generate_ending(article: Article, steps: list[StoryStep]) -> Ending:
    ending = await gemma_engine.generate_ending(article, steps)
    return Ending.model_validate(ending.model_dump())
