"""Gemma Service Package.

Exposes:
- generate_scene(article, steps, turn) -> Scene
- generate_ending(article, steps) -> Ending
- GemmaStoryEngine
- Schema models
"""
from .engine import GemmaStoryEngine, generate_ending, generate_scene
from .schemas import Article, Choice, Ending, HealthResponse, Scene, StoryStep

__all__ = [
    "GemmaStoryEngine",
    "generate_scene",
    "generate_ending",
    "Article",
    "Choice",
    "Scene",
    "Ending",
    "StoryStep",
    "HealthResponse",
]
