"""Official Wikipedia REST API only (no scraping). Owner: Member 3."""
from urllib.parse import quote
import httpx
from .config import get_settings
from .errors import AppError
from .schemas import Article

RANDOM_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/random/summary"
MIN_EXTRACT_CHARS = 300
MAX_EXTRACT_CHARS = 1800
MAX_ATTEMPTS = 6
SKIP_TITLE_PREFIXES = ("List of", "Lists of", "Index of", "Outline of", "Timeline of")
# A basic filter so a school demo does not open on distressing topics. Extend as needed.
UNSUITABLE_TERMS = (
    "pornograph", "sexual assault", "rape", "suicide", "child abuse",
    "genocide", "terroris", "paedophil", "pedophil",
)


def is_suitable(data: dict) -> bool:
    title = str(data.get("title", ""))
    extract = str(data.get("extract", "")).strip()
    if data.get("type") != "standard":  # skips disambiguation pages, redirects, errors
        return False
    if len(extract) < MIN_EXTRACT_CHARS:  # stubs make boring stories
        return False
    if title.startswith(SKIP_TITLE_PREFIXES) or "(disambiguation)" in title:
        return False
    lowered = extract.lower()
    return not any(term in lowered for term in UNSUITABLE_TERMS)


def to_article(data: dict) -> Article:
    extract = " ".join(str(data["extract"]).split())
    if len(extract) > MAX_EXTRACT_CHARS:
        cut = extract[:MAX_EXTRACT_CHARS]
        extract = cut[: cut.rfind(". ") + 1] if ". " in cut else cut
    title = str(data["title"])
    url = (data.get("content_urls", {}).get("desktop", {}) or {}).get("page")
    return Article(
        title=title,
        extract=extract,
        url=url or f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}",
        thumbnail_url=(data.get("thumbnail") or {}).get("source"),
    )


async def fetch_random_article(transport: httpx.AsyncBaseTransport | None = None) -> Article:
    """Try up to MAX_ATTEMPTS random articles and return the first suitable one."""
    headers = {"User-Agent": get_settings().wiki_user_agent, "Accept": "application/json"}
    async with httpx.AsyncClient(
        headers=headers, timeout=8.0, follow_redirects=True, transport=transport
    ) as client:
        for _ in range(MAX_ATTEMPTS):
            try:
                response = await client.get(RANDOM_SUMMARY_URL)
                response.raise_for_status()
                data = response.json()
            except (httpx.HTTPError, ValueError):
                raise AppError(
                    "WIKIPEDIA_UNAVAILABLE",
                    "Wikipedia did not respond. Please try again in a moment.",
                    502,
                    True,
                ) from None
            if is_suitable(data):
                return to_article(data)
    raise AppError(
        "NO_SUITABLE_ARTICLE",
        "We could not find a good article this time. Please try again.",
        503,
        True,
    )
