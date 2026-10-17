from gemma_service.prompts import (
    build_ending_prompt,
    build_scene_prompt,
    format_history,
)
from gemma_service.schemas import Article, Choice, StoryStep


def test_format_history_empty():
    assert "no prior turns" in format_history([])


def test_format_history_with_steps():
    steps = [
        StoryStep(
            turn=1,
            narrative="You found an old clock.",
            choices=[Choice(id="A", text="Wind it"), Choice(id="B", text="Ignore it"), Choice(id="C", text="Break it")],
            chosen_id="A",
            chosen_text="Wind it",
        )
    ]
    formatted = format_history(steps)
    assert "Turn 1" in formatted
    assert "Wind it" in formatted


def test_build_scene_prompt():
    art = Article(
        title="Rosetta Stone",
        extract="The Rosetta Stone is a stele inscribed with three versions of a decree.",
        url="https://en.wikipedia.org/wiki/Rosetta_Stone",
    )
    prompt = build_scene_prompt(art, [], turn=1)
    assert "Rosetta Stone" in prompt
    assert "Current Turn: 1 of 5" in prompt
    assert "choices" in prompt


def test_build_ending_prompt():
    art = Article(
        title="Rosetta Stone",
        extract="The Rosetta Stone is a stele inscribed with three versions of a decree.",
        url="https://en.wikipedia.org/wiki/Rosetta_Stone",
    )
    prompt = build_ending_prompt(art, [])
    assert "Topic: Rosetta Stone" in prompt
    assert "epilogue" in prompt.lower()
