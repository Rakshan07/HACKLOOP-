"""Owner: Member 3. Uses a fake HTTP transport, so no real Wikipedia calls are made."""
import httpx
import pytest
from app import wikipedia
from app.errors import AppError
from .fakes import GOOD_TEXT


def summary(title="Real Place", extract=GOOD_TEXT, type_="standard"):
    return {
        "type": type_,
        "title": title,
        "extract": extract,
        "content_urls": {"desktop": {"page": f"https://en.wikipedia.org/wiki/{title}"}},
        "thumbnail": {"source": "https://upload.wikimedia.org/x.jpg"},
    }


def transport_for(responses):
    queue = list(responses)
    seen = []

    def handler(request: httpx.Request):
        seen.append(request)
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return httpx.Response(200, json=item)

    return httpx.MockTransport(handler), seen


@pytest.mark.anyio
async def test_returns_first_suitable_article_and_sends_user_agent():
    transport, seen = transport_for([summary()])
    article = await wikipedia.fetch_random_article(transport)
    assert article.title == "Real Place"
    assert article.thumbnail_url.startswith("https://upload.wikimedia.org")
    assert "RabbitHole" in seen[0].headers["user-agent"]


@pytest.mark.anyio
async def test_skips_stubs_disambiguation_and_lists():
    bad = [
        summary(extract="Too short."),
        summary(type_="disambiguation"),
        summary(title="List of lighthouses"),
        summary(extract=GOOD_TEXT + " It involved sexual assault."),
    ]
    transport, seen = transport_for([*bad, summary(title="Good One")])
    article = await wikipedia.fetch_random_article(transport)
    assert article.title == "Good One"
    assert len(seen) == 5


@pytest.mark.anyio
async def test_gives_up_after_bounded_attempts():
    transport, seen = transport_for([summary(extract="short")] * wikipedia.MAX_ATTEMPTS)
    with pytest.raises(AppError) as err:
        await wikipedia.fetch_random_article(transport)
    assert err.value.code == "NO_SUITABLE_ARTICLE"
    assert len(seen) == wikipedia.MAX_ATTEMPTS


@pytest.mark.anyio
async def test_network_failure_becomes_friendly_error():
    transport, _ = transport_for([httpx.ConnectError("boom")])
    with pytest.raises(AppError) as err:
        await wikipedia.fetch_random_article(transport)
    assert err.value.code == "WIKIPEDIA_UNAVAILABLE"
    assert err.value.retryable is True


def test_long_extract_is_trimmed_at_a_sentence_and_url_has_fallback():
    long_text = "A sentence about lighthouses. " * 200
    data = summary(extract=long_text)
    del data["content_urls"]
    article = wikipedia.to_article(data)
    assert len(article.extract) <= wikipedia.MAX_EXTRACT_CHARS
    assert article.extract.endswith(".")
    assert article.url.startswith("https://en.wikipedia.org/wiki/")
