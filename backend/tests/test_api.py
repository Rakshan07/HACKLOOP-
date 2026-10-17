"""Owner: Member 3. Wikipedia and Gemma are replaced by fakes: this tests OUR game rules."""
import asyncio
import httpx
import pytest
from app import game_service
from app.errors import AppError
from app.main import app
from .fakes import ARTICLE, ending, scene


@pytest.fixture
def calls(monkeypatch):
    counter = {"wiki": 0, "scene": 0, "ending": 0}

    async def fake_article():
        counter["wiki"] += 1
        return ARTICLE

    async def fake_scene(article, steps, turn):
        counter["scene"] += 1
        await asyncio.sleep(0.05)  # slow enough that duplicate requests overlap
        return scene(turn)

    async def fake_ending(article, steps):
        counter["ending"] += 1
        return ending()

    monkeypatch.setattr(game_service.wikipedia, "fetch_random_article", fake_article)
    monkeypatch.setattr(game_service.story_engine, "generate_scene", fake_scene)
    monkeypatch.setattr(game_service.story_engine, "generate_ending", fake_ending)
    return counter


def client():
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def new_started_game(c):
    created = (await c.post("/api/games")).json()
    return (await c.post(f"/api/games/{created['gameId']}/start")).json()


@pytest.mark.anyio
async def test_create_then_start_gives_playable_first_scene(calls):
    async with client() as c:
        created = await c.post("/api/games")
        assert created.status_code == 201
        assert created.json()["status"] == "ARTICLE_READY"
        game = (await c.post(f"/api/games/{created.json()['gameId']}/start")).json()
        assert game["status"] == "PLAYING" and game["turn"] == 1
        assert [ch["id"] for ch in game["scene"]["choices"]] == ["A", "B", "C"]  # exactly three
        assert game["article"]["url"].startswith("https://en.wikipedia.org/")


@pytest.mark.anyio
async def test_start_twice_calls_gemma_once(calls):
    async with client() as c:
        gid = (await c.post("/api/games")).json()["gameId"]
        await asyncio.gather(c.post(f"/api/games/{gid}/start"), c.post(f"/api/games/{gid}/start"))
        assert calls["scene"] == 1


@pytest.mark.anyio
@pytest.mark.parametrize("letter", ["A", "B", "C"])
async def test_every_valid_choice_advances_the_game(calls, letter):
    async with client() as c:
        game = await new_started_game(c)
        nxt = (await c.post(f"/api/games/{game['gameId']}/choices", json={"turn": 1, "choiceId": letter})).json()
        assert nxt["turn"] == 2 and nxt["scene"]["turn"] == 2
        assert nxt["history"] == [{"turn": 1, "choiceId": letter, "choiceText": game["scene"]["choices"]["ABC".index(letter)]["text"]}]


@pytest.mark.anyio
async def test_game_ends_after_exactly_five_decisions(calls):
    async with client() as c:
        game = await new_started_game(c)
        gid = game["gameId"]
        for turn in range(1, 5):
            game = (await c.post(f"/api/games/{gid}/choices", json={"turn": turn, "choiceId": "A"})).json()
            assert game["status"] == "PLAYING" and game["turn"] == turn + 1
        final = (await c.post(f"/api/games/{gid}/choices", json={"turn": 5, "choiceId": "B"})).json()
        assert final["status"] == "COMPLETED"
        assert final["ending"]["title"] and len(final["history"]) == 5
        again = await c.post(f"/api/games/{gid}/choices", json={"turn": 5, "choiceId": "A"})
        assert again.status_code == 409 and again.json()["error"]["code"] == "GAME_NOT_PLAYING"
        assert calls["scene"] == 5 and calls["ending"] == 1


@pytest.mark.anyio
async def test_duplicate_simultaneous_submission_advances_only_one_turn(calls):
    async with client() as c:
        game = await new_started_game(c)
        url = f"/api/games/{game['gameId']}/choices"
        body = {"turn": 1, "choiceId": "A"}
        r1, r2 = await asyncio.gather(c.post(url, json=body), c.post(url, json=body))
        assert sorted([r1.status_code, r2.status_code]) == [200, 409]
        loser = r1 if r1.status_code == 409 else r2
        assert loser.json()["error"]["code"] == "STALE_TURN"
        state = (await c.get(f"/api/games/{game['gameId']}")).json()
        assert state["turn"] == 2 and len(state["history"]) == 1
        assert calls["scene"] == 2  # opening + exactly one next scene


@pytest.mark.anyio
async def test_choose_before_start_is_rejected(calls):
    async with client() as c:
        gid = (await c.post("/api/games")).json()["gameId"]
        r = await c.post(f"/api/games/{gid}/choices", json={"turn": 1, "choiceId": "A"})
        assert r.status_code == 409 and r.json()["error"]["code"] == "GAME_NOT_PLAYING"


@pytest.mark.anyio
async def test_malformed_requests_are_rejected_with_standard_error(calls):
    async with client() as c:
        game = await new_started_game(c)
        url = f"/api/games/{game['gameId']}/choices"
        bad_bodies = [
            {"turn": 1, "choiceId": "Z"},
            {"turn": 0, "choiceId": "A"},
            {"turn": 1, "choiceId": "A", "extra": "nope"},
            {"choiceId": "A"},
            {},
        ]
        for body in bad_bodies:
            r = await c.post(url, json=body)
            assert r.status_code == 422, body
            assert r.json()["error"]["code"] == "BAD_REQUEST"
        not_json = await c.post(url, content=b"not json", headers={"content-type": "application/json"})
        assert not_json.status_code == 422
        missing = await c.get("/api/games/doesnotexist")
        assert missing.status_code == 404 and missing.json()["error"]["code"] == "GAME_NOT_FOUND"
        state = (await c.get(f"/api/games/{game['gameId']}")).json()
        assert state["turn"] == 1  # nothing above changed the game


@pytest.mark.anyio
async def test_restart_keeps_topic_and_new_adventure_fetches_fresh_article(calls):
    async with client() as c:
        game = await new_started_game(c)
        same = (await c.post(f"/api/games/{game['gameId']}/restart")).json()
        assert same["gameId"] != game["gameId"]
        assert same["article"]["title"] == game["article"]["title"]
        assert same["status"] == "ARTICLE_READY" and same["history"] == []
        fresh = (await c.post("/api/games")).json()
        assert fresh["gameId"] not in (game["gameId"], same["gameId"])
        assert calls["wiki"] == 2  # restart did NOT fetch again


@pytest.mark.anyio
async def test_refresh_returns_the_same_state(calls):
    async with client() as c:
        game = await new_started_game(c)
        await c.post(f"/api/games/{game['gameId']}/choices", json={"turn": 1, "choiceId": "C"})
        first = (await c.get(f"/api/games/{game['gameId']}")).json()
        second = (await c.get(f"/api/games/{game['gameId']}")).json()
        assert first == second and first["turn"] == 2


@pytest.mark.anyio
async def test_gemma_failure_returns_friendly_error_and_keeps_state(monkeypatch, calls):
    async with client() as c:
        game = await new_started_game(c)

        async def timeout(*_args):
            raise AppError("GEMMA_TIMEOUT", "The narrator is taking too long. Please try again.", 504, True)

        real = game_service.story_engine.generate_scene
        monkeypatch.setattr(game_service.story_engine, "generate_scene", timeout)
        r = await c.post(f"/api/games/{game['gameId']}/choices", json={"turn": 1, "choiceId": "A"})
        assert r.status_code == 504
        assert r.json() == {"error": {"code": "GEMMA_TIMEOUT", "message": "The narrator is taking too long. Please try again.", "retryable": True}}
        assert (await c.get(f"/api/games/{game['gameId']}")).json()["turn"] == 1
        monkeypatch.setattr(game_service.story_engine, "generate_scene", real)  # retry now works
        ok = await c.post(f"/api/games/{game['gameId']}/choices", json={"turn": 1, "choiceId": "A"})
        assert ok.status_code == 200 and ok.json()["turn"] == 2


@pytest.mark.anyio
async def test_many_games_in_parallel_do_not_mix_state(calls):
    async def play(letter):
        async with client() as c:
            game = await new_started_game(c)
            gid = game["gameId"]
            for turn in range(1, 6):
                game = (await c.post(f"/api/games/{gid}/choices", json={"turn": turn, "choiceId": letter})).json()
            return game

    results = await asyncio.gather(*(play(letter) for letter in "ABCABC"))
    assert all(g["status"] == "COMPLETED" and len(g["history"]) == 5 for g in results)
    for game, letter in zip(results, "ABCABC"):
        assert {h["choiceId"] for h in game["history"]} == {letter}
    assert len({g["gameId"] for g in results}) == 6


@pytest.mark.anyio
async def test_api_key_is_never_exposed(calls):
    async with client() as c:
        health = await c.get("/api/health")
        missing = await c.get("/api/games/nope")
        for response in (health, missing):
            assert "test-key-not-real" not in response.text
        assert health.json()["aiConfigured"] is True
