"""Settings read from environment variables (see .env.example). Owner: Member 3."""
import os
from dataclasses import dataclass
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemma_model: str
    gemma_timeout_seconds: float
    gemma_max_output_tokens: int
    wiki_user_agent: str
    cors_origins: list[str]
    game_ttl_seconds: int
    max_games: int


@lru_cache
def get_settings() -> Settings:
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemma_model=os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it").strip(),
        gemma_timeout_seconds=float(os.getenv("GEMMA_TIMEOUT_SECONDS", "40")),
        gemma_max_output_tokens=int(os.getenv("GEMMA_MAX_OUTPUT_TOKENS", "1500")),
        wiki_user_agent=os.getenv(
            "WIKI_USER_AGENT", "RabbitHole/1.0 (hackathon project; set WIKI_USER_AGENT)"
        ),
        cors_origins=[o.strip() for o in origins.split(",") if o.strip()],
        game_ttl_seconds=int(os.getenv("GAME_TTL_SECONDS", "7200")),
        max_games=int(os.getenv("MAX_GAMES", "500")),
    )
