import pytest
from pydantic import ValidationError
from gemma_service.schemas import (
    Article,
    Choice,
    Ending,
    GenerateEndingRequest,
    GenerateSceneRequest,
    Scene,
    StoryStep,
)


def test_article_camel_serialization():
    art = Article(
        title="Antarctica",
        extract="Cold continent",
        url="https://en.wikipedia.org/wiki/Antarctica",
        thumbnail_url="https://example.com/thumb.jpg",
    )
    dumped = art.model_dump(by_alias=True)
    assert dumped["thumbnailUrl"] == "https://example.com/thumb.jpg"
    assert dumped["title"] == "Antarctica"


def test_scene_choice_validation():
    choices = [
        Choice(id="A", text="Choice A"),
        Choice(id="B", text="Choice B"),
        Choice(id="C", text="Choice C"),
    ]
    scene = Scene(turn=1, narrative="Story begins...", choices=choices, fact="A fun fact")
    assert scene.turn == 1
    assert len(scene.choices) == 3

    # Invalid choice id should raise ValidationError
    with pytest.raises(ValidationError):
        Choice(id="D", text="Invalid choice")  # type: ignore


def test_story_step():
    step = StoryStep(
        turn=1,
        narrative="Opening scene",
        choices=[
            Choice(id="A", text="Left"),
            Choice(id="B", text="Right"),
            Choice(id="C", text="Forward"),
        ],
        chosen_id="B",
        chosen_text="Right",
    )
    assert step.chosen_id == "B"
    assert step.turn == 1


def test_generate_ending_request_min_length():
    art = Article(title="Test", extract="Extract", url="https://example.com")
    # Empty steps should fail validation
    with pytest.raises(ValidationError):
        GenerateEndingRequest(article=art, steps=[])
