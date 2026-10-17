"""In-memory game sessions (no database needed for the MVP). Owner: Member 3."""
import asyncio
import time
import uuid
from dataclasses import dataclass, field
from .errors import AppError
from .schemas import Article, Ending, Scene, StoryStep


@dataclass
class Game:
    id: str
    article: Article
    status: str = "ARTICLE_READY"  # ARTICLE_READY -> PLAYING -> COMPLETED
    turn: int = 1  # the turn the player is currently on (1..5)
    scene: Scene | None = None
    ending: Ending | None = None
    steps: list[StoryStep] = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)  # one action per game at a time
    updated_at: float = field(default_factory=time.time)

    def touch(self) -> None:
        self.updated_at = time.time()


class SessionStore:
    def __init__(self, ttl_seconds: int, max_games: int):
        self._games: dict[str, Game] = {}
        self._ttl = ttl_seconds
        self._max = max_games

    def create(self, article: Article) -> Game:
        self._purge()
        game = Game(id=uuid.uuid4().hex, article=article)
        self._games[game.id] = game
        return game

    def get(self, game_id: str) -> Game:
        game = self._games.get(game_id)
        if game is None or time.time() - game.updated_at > self._ttl:
            self._games.pop(game_id, None)
            raise AppError(
                "GAME_NOT_FOUND", "That adventure has expired. Start a new one.", 404, False
            )
        return game

    def clear(self) -> None:
        self._games.clear()

    def __len__(self) -> int:
        return len(self._games)

    def _purge(self) -> None:
        now = time.time()
        for gid in [g.id for g in self._games.values() if now - g.updated_at > self._ttl]:
            del self._games[gid]
        while len(self._games) >= self._max:  # drop the oldest if we are full
            oldest = min(self._games.values(), key=lambda g: g.updated_at)
            del self._games[oldest.id]
