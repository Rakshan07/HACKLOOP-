"""Configuration for Gemma Service."""
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
    gemma_temperature: float
    mock_mode: bool
    host: str
    port: int
    debug: bool


@lru_cache
def get_settings() -> Settings:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    mock_mode_env = os.getenv("GEMMA_MOCK_MODE", "false").lower() in ("true", "1", "yes")

    # If no API key is provided, enable mock_mode automatically for smooth developer experience
    mock_mode = mock_mode_env or (len(api_key) == 0)

    return Settings(
        gemini_api_key=api_key,
        gemma_model=os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it").strip(),
        gemma_timeout_seconds=float(os.getenv("GEMMA_TIMEOUT_SECONDS", "40.0")),
        gemma_max_output_tokens=int(os.getenv("GEMMA_MAX_OUTPUT_TOKENS", "1500")),
        gemma_temperature=float(os.getenv("GEMMA_TEMPERATURE", "0.7")),
        mock_mode=mock_mode,
        host=os.getenv("HOST", "0.0.0.0").strip(),
        port=int(os.getenv("PORT", "8001")),
        debug=os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
    )
