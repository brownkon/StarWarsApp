"""FastAPI backend for the Star Wars Data Explorer vertical slice."""
import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Set

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

SWAPI_PEOPLE_URL = "https://swapi.dev/api/people/"
DB_PATH = Path(__file__).resolve().parent / "swapi_cache.db"

app = FastAPI(title="Star Wars Data Explorer", version="0.1.0")

# Allow local dev from the React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Character(BaseModel):
    name: str
    height_cm: Optional[float]
    height_in: Optional[float]
    mass_kg: Optional[float]
    birth_year: Optional[str]
    gender: Optional[str]
    hair_color: Optional[str]
    eye_color: Optional[str]
    homeworld: Optional[str]
    homeworld_name: Optional[str] = None
    films: List[str]
    film_titles: List[str] = []
    species: List[str]
    species_names: List[str] = []
    starships: List[str]
    starship_names: List[str] = []
    url: Optional[str]


class ResolveRequest(BaseModel):
    homeworld: Optional[str] = None
    films: List[str] = []
    species: List[str] = []
    starships: List[str] = []


class ResolveResponse(BaseModel):
    homeworld: Optional[str]
    films: List[str]
    species: List[str]
    starships: List[str]


def _to_float(value: str) -> Optional[float]:
    """Parse numeric strings while ignoring unknowns and commas."""
    if value is None:
        return None
    value = value.replace(",", "").strip().lower()
    if not value or value == "unknown":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _cm_to_inches(height_cm: Optional[float]) -> Optional[float]:
    if height_cm is None:
        return None
    return round(height_cm / 2.54, 1)


def _transform_character(raw: dict) -> dict:
    height_cm = _to_float(raw.get("height"))
    mass_kg = _to_float(raw.get("mass"))

    return {
        "name": raw.get("name", "Unknown"),
        "height_cm": height_cm,
        "height_in": _cm_to_inches(height_cm),
        "mass_kg": mass_kg,
        "birth_year": raw.get("birth_year"),
        "gender": raw.get("gender"),
        "hair_color": raw.get("hair_color"),
        "eye_color": raw.get("eye_color"),
        "homeworld": raw.get("homeworld"),
        "films": raw.get("films", []),
        "species": raw.get("species", []),
        "starships": raw.get("starships", []),
        "url": raw.get("url"),
    }


def _init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS characters (
                name TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resolved_names (
                url TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()


def _load_cached_characters() -> List[dict]:
    if not DB_PATH.exists():
        return []
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT payload FROM characters").fetchall()
    return [_ensure_display_fields(json.loads(row[0])) for row in rows]


def _replace_cache(characters: List[dict]) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM characters")
        conn.executemany(
            "INSERT INTO characters (name, payload) VALUES (?, ?)",
            [(char["name"], json.dumps(_ensure_display_fields(char))) for char in characters],
        )
        conn.commit()


def _ensure_display_fields(char: dict) -> dict:
    """Ensure name/title fields exist to satisfy the response model."""
    char.setdefault("homeworld_name", None)
    char.setdefault("film_titles", [])
    char.setdefault("species_names", [])
    char.setdefault("starship_names", [])
    return char


def _load_cached_names(urls: Set[str]) -> Dict[str, str]:
    if not urls:
        return {}
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT url, name FROM resolved_names WHERE url IN (%s)"
            % ",".join(["?"] * len(urls)),
            list(urls),
        ).fetchall()
    return {url: name for url, name in rows}


def _store_names(pairs: Dict[str, str]) -> None:
    if not pairs:
        return
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "INSERT OR REPLACE INTO resolved_names (url, name) VALUES (?, ?)",
            [(url, name) for url, name in pairs.items()],
        )
        conn.commit()


def _sorting_key(field: str):
    def key(item: dict):
        value = item.get(field)
        is_missing = value is None
        comparable = value
        if isinstance(value, str):
            comparable = value.lower()
        return (is_missing, comparable)

    return key


async def _fetch_people() -> List[dict]:
    """Fetch all people pages from SWAPI."""
    results: List[dict] = []
    next_url: Optional[str] = SWAPI_PEOPLE_URL
    page_counter = 0

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            while next_url:
                response = await client.get(next_url)
                response.raise_for_status()
                payload = response.json()
                results.extend(payload.get("results", []))
                next_url = payload.get("next")
                page_counter += 1
                if page_counter > 10:  # guard against runaway pagination
                    break
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"SWAPI returned an error: {exc.response.status_code}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=504,
            detail="Unable to reach SWAPI. Please try again shortly.",
        ) from exc

    return results


async def _get_characters_from_source(refresh: bool) -> List[dict]:
    """Return characters, using cache unless refresh is requested or cache empty."""
    cached = [] if refresh else _load_cached_characters()
    if cached:
        if _needs_name_enrichment(cached):
            enriched_cached = await _enrich_with_names(cached)
            _replace_cache(enriched_cached)
            return enriched_cached
        return cached

    raw_people = await _fetch_people()
    simplified = [_transform_character(person) for person in raw_people]
    enriched = await _enrich_with_names(simplified)
    _replace_cache(enriched)
    return enriched


async def _enrich_with_names(characters: List[dict]) -> List[dict]:
    """Attach name lookups (homeworld, films, species, starships) using the cache."""
    url_set: Set[str] = set()
    for char in characters:
        url_set.update(filter(None, [char.get("homeworld")]))
        for key in ("films", "species", "starships"):
            url_set.update(char.get(key, []))

    resolved = await _resolve_urls(url_set)

    for char in characters:
        char["homeworld_name"] = resolved.get(char.get("homeworld"))
        char["film_titles"] = [resolved.get(url) for url in char.get("films", []) if resolved.get(url)]
        char["species_names"] = [resolved.get(url) for url in char.get("species", []) if resolved.get(url)]
        char["starship_names"] = [resolved.get(url) for url in char.get("starships", []) if resolved.get(url)]

    return [_ensure_display_fields(char) for char in characters]


def _needs_name_enrichment(characters: List[dict]) -> bool:
    """Detect if any character is missing resolved display names."""
    for char in characters:
        if char.get("homeworld") and not char.get("homeworld_name"):
            return True
        if char.get("films") and not char.get("film_titles"):
            return True
        if char.get("species") and not char.get("species_names"):
            return True
        if char.get("starships") and not char.get("starship_names"):
            return True
    return False


async def _fetch_name(client: httpx.AsyncClient, url: str) -> Optional[str]:
    """Fetch a resource by URL and return its name/title field."""
    try:
        response = await client.get(url)
        response.raise_for_status()
        payload = response.json()
        return payload.get("name") or payload.get("title")
    except Exception:
        return None


async def _resolve_urls(urls: Set[str]) -> Dict[str, str]:
    """Resolve a set of URLs to names using cache first, then SWAPI."""
    urls = {u for u in urls if u}
    if not urls:
        return {}

    cached = _load_cached_names(urls)
    missing = [u for u in urls if u not in cached]
    fresh: Dict[str, Optional[str]] = {}

    if missing:
        async with httpx.AsyncClient(timeout=10) as client:
            results = await asyncio.gather(*[_fetch_name(client, url) for url in missing])
        fresh = {url: name for url, name in zip(missing, results) if name}
        if fresh:
            _store_names(fresh)

    combined = {**cached, **fresh}
    return combined


@app.get("/api/characters", response_model=List[Character])
async def list_characters(
    sort_by: str = Query(
        "mass_kg",
        enum=["name", "height_cm", "mass_kg", "birth_year", "gender", "homeworld"],
        description="Server-side sort field",
    ),
    order: str = Query("desc", enum=["asc", "desc"], description="Sort order"),
    refresh: bool = Query(False, description="Force refresh from SWAPI and repopulate cache"),
):
    """Fetch characters from SWAPI, simplify the shape, and sort before returning."""

    simplified = await _get_characters_from_source(refresh)

    reverse = order == "desc"
    simplified.sort(key=_sorting_key(sort_by), reverse=reverse)
    return simplified


@app.on_event("startup")
def startup_event():
    _init_db()


@app.post("/api/resolve", response_model=ResolveResponse)
async def resolve_entities(payload: ResolveRequest):
    """Resolve SWAPI resource URLs to their display names, concurrently."""

    urls: Set[str] = set()
    urls.update(filter(None, [payload.homeworld]))
    urls.update(payload.films)
    urls.update(payload.species)
    urls.update(payload.starships)

    resolved = await _resolve_urls(urls)

    homeworld_name = resolved.get(payload.homeworld) if payload.homeworld else None
    films = [resolved.get(url) for url in payload.films if resolved.get(url)]
    species = [resolved.get(url) for url in payload.species if resolved.get(url)]
    starships = [resolved.get(url) for url in payload.starships if resolved.get(url)]

    return ResolveResponse(
        homeworld=homeworld_name,
        films=films,
        species=species,
        starships=starships,
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    _init_db()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
