import pytest
from gemma_service.config import Settings
from gemma_service.engine import GemmaStoryEngine
from gemma_service.schemas import Article, Choice, StoryStep


@pytest.fixture
def mock_settings():
    return Settings(
        gemini_api_key="",
        gemma_model="gemma-4-26b-a4b-it",
        gemma_timeout_seconds=5.0,
        gemma_max_output_tokens=500,
        gemma_temperature=0.7,
        mock_mode=True,
        host="127.0.0.1",
        port=8001,
        debug=True,
    )


@pytest.fixture
def sample_article():
    return Article(
        title="Voyager 1",
        extract="Voyager 1 is a space probe launched by NASA on September 5, 1977. Part of the Voyager program to study the outer Solar System.",
        url="https://en.wikipedia.org/wiki/Voyager_1",
    )


@pytest.mark.asyncio
async def test_generate_scene_fallback(mock_settings, sample_article):
    engine = GemmaStoryEngine(mock_settings)
    scene = await engine.generate_scene(sample_article, [], 1)

    assert scene.turn == 1
    assert "Voyager 1" in scene.narrative
    assert len(scene.choices) == 3
    assert {c.id for c in scene.choices} == {"A", "B", "C"}
    assert len(scene.fact) > 5


@pytest.mark.asyncio
async def test_generate_ending_fallback(mock_settings, sample_article):
    engine = GemmaStoryEngine(mock_settings)
    steps = [
        StoryStep(
            turn=1,
            narrative="Turn 1 scene",
            choices=[Choice(id="A", text="Inspect instruments"), Choice(id="B", text="Boost signal"), Choice(id="C", text="Enter sleep mode")],
            chosen_id="A",
            chosen_text="Inspect instruments",
        )
    ]
    ending = await engine.generate_ending(sample_article, steps)

    assert "Voyager 1" in ending.title
    assert len(ending.narrative) > 20
    assert len(ending.lesson) > 10
