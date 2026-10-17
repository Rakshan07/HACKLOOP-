"""Game rules and state transitions. The backend is the authority on turns. Owner: Member 3.

Story text comes from Member 4's story_engine; this file only enforces the rules.
"""
from . import story_engine, wikipedia
from .config import get_settings
from .errors import AppError
from .schemas import TOTAL_TURNS, GameView, HistoryItem, StoryStep
from .sessions import Game, SessionStore

_settings = get_settings()
store = SessionStore(_settings.game_ttl_seconds, _settings.max_games)


def to_view(game: Game) -> GameView:
    return GameView(
        game_id=game.id,
        status=game.status,
        turn=game.turn,
        total_turns=TOTAL_TURNS,
        article=game.article,
        scene=game.scene,
        ending=game.ending,
        history=[
            HistoryItem(turn=s.turn, choice_id=s.chosen_id, choice_text=s.chosen_text)
            for s in game.steps
        ],
    )


async def create_game() -> GameView:
    """Step 1: fetch a random Wikipedia article and open a session."""
    article = await wikipedia.fetch_random_article()
    return to_view(store.create(article))


async def restart_same_topic(game_id: str) -> GameView:
    """Same article, brand-new session."""
    old = store.get(game_id)
    return to_view(store.create(old.article))


def get_view(game_id: str) -> GameView:
    return to_view(store.get(game_id))


async def begin(game_id: str) -> GameView:
    """Step 2: ask Gemma for the opening scene. Safe to call twice (no duplicate AI call)."""
    game = store.get(game_id)
    async with game.lock:
        if game.scene is None and game.status == "ARTICLE_READY":
            scene = await story_engine.generate_scene(game.article, [], 1)
            game.scene = scene
            game.status = "PLAYING"
            game.touch()
    return to_view(game)


async def choose(game_id: str, turn: int, choice_id: str) -> GameView:
    """Step 3: apply one player decision. State only changes after Gemma succeeds."""
    game = store.get(game_id)
    async with game.lock:  # a duplicate click waits here, then fails the turn check below
        if game.status != "PLAYING" or game.scene is None:
            raise AppError(
                "GAME_NOT_PLAYING", "This adventure is not waiting for a choice.", 409, False
            )
        if turn != game.turn:
            raise AppError(
                "STALE_TURN",
                "That choice was for an earlier scene. Refreshing the story.",
                409,
                False,
            )
        picked = next((c for c in game.scene.choices if c.id == choice_id), None)
        if picked is None:
            raise AppError("INVALID_CHOICE", "That is not one of the options.", 422, False)
        step = StoryStep(
            turn=game.turn,
            narrative=game.scene.narrative,
            choices=game.scene.choices,
            chosen_id=picked.id,
            chosen_text=picked.text,
        )
        steps = [*game.steps, step]
        if game.turn >= TOTAL_TURNS:  # fifth decision: write the ending
            ending = await story_engine.generate_ending(game.article, steps)
            game.steps = steps
            game.ending = ending
            game.status = "COMPLETED"
        else:
            scene = await story_engine.generate_scene(game.article, steps, game.turn + 1)
            game.steps = steps
            game.scene = scene
            game.turn += 1
        game.touch()
        return to_view(game)
