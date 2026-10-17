import os

os.environ.setdefault("GEMINI_API_KEY", "test-key-not-real")

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_store():
    from app import game_service

    game_service.store.clear()
    yield
    game_service.store.clear()


@pytest.fixture
def anyio_backend():
    return "asyncio"
