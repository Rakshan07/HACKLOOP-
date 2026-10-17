"""Shared fake data for tests."""
from app.schemas import Article, Choice, Ending, Scene

GOOD_TEXT = "The lighthouse keeper recorded every storm in a leather logbook. " * 8
ARTICLE = Article(
    title="Test Lighthouse",
    extract=GOOD_TEXT.strip(),
    url="https://en.wikipedia.org/wiki/Test_Lighthouse",
)


def scene(turn: int) -> Scene:
    return Scene(
        turn=turn,
        narrative=f"Scene number {turn}. You stand on a windy cliff and must decide what to do next.",
        choices=[
            Choice(id="A", text="Climb the tower"),
            Choice(id="B", text="Read the logbook"),
            Choice(id="C", text="Signal the ships"),
        ],
        fact="The keeper recorded every storm.",
    )


def ending() -> Ending:
    return Ending(
        title="The Last Light",
        narrative="You finally understand why the keeper wrote everything down. The sea rests.",
        lesson="The keeper recorded storms in a logbook. Records like this help historians today.",
    )
