import json
import urllib.error
import urllib.parse
import urllib.request

WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
TIMEOUT_SECONDS = 8
USER_AGENT = "Bookly/1.0 (bookstore assistant chatbot)"


def fetch_summary(title: str, author: str | None = None) -> dict:
    """Look up a book's Wikipedia summary and return the intro extract.

    Tries `<title> (novel)` first (handles disambiguated books like Dune,
    1984), falls back to `<title>` alone (unambiguous books like The Hobbit),
    then finally to a full-text search. Returns `found: false` with a clear
    error if no book-like page can be located.
    """
    if not title:
        return {"found": False, "error": "title is required"}

    for candidate in (f"{title} (novel)", title):
        result = _fetch_summary_by_title(candidate)
        if _looks_like_book_page(result, author):
            return result

    query = f'"{title}" novel'
    if author:
        query += f" {author}"
    page_title = _search_for_page(query)
    if page_title:
        result = _fetch_summary_by_title(page_title)
        if _looks_like_book_page(result, author):
            return result

    label = f'"{title}"' + (f" by {author}" if author else "")
    return {
        "found": False,
        "error": "not_found",
        "message": f"No Wikipedia article for a book titled {label} was found.",
    }


def _looks_like_book_page(result: dict, author: str | None) -> bool:
    if not result.get("found") or result.get("is_disambiguation"):
        return False
    desc = (result.get("description") or "").lower()
    extract = (result.get("summary") or "")[:600].lower()
    if any(kw in desc for kw in ("novel", "book", "novella", "memoir")):
        return True
    if any(kw in extract for kw in (" novel", " book ", " novella", " memoir")):
        return True
    if author and author.lower() in extract:
        return True
    return False


def _search_for_page(query: str) -> str | None:
    params = {
        "action": "query",
        "list": "search",
        "format": "json",
        "srsearch": query,
        "srlimit": "1",
        "srnamespace": "0",
    }
    url = f"{WIKI_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError):
        return None

    results = ((data.get("query") or {}).get("search")) or []
    return results[0]["title"] if results else None


def _fetch_summary_by_title(page_title: str) -> dict:
    encoded = urllib.parse.quote(page_title.replace(" ", "_"), safe="")
    url = f"{WIKI_SUMMARY_URL}{encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"found": False, "error": "not_found"}
        return {"found": False, "error": f"http error {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"found": False, "error": f"network error: {e}"}
    except json.JSONDecodeError as e:
        return {"found": False, "error": f"invalid response from Wikipedia: {e}"}

    page_type = data.get("type")
    return {
        "found": True,
        "title": data.get("title"),
        "description": data.get("description"),
        "summary": data.get("extract"),
        "url": (data.get("content_urls") or {}).get("desktop", {}).get("page"),
        "type": page_type,
        "is_disambiguation": page_type == "disambiguation",
    }
