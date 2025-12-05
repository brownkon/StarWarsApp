"""FastAPI backend for the Star Wars Data Explorer vertical slice."""
import asyncio
import json
import sqlite3
from pathlib import Path
from typing import List, Optional

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
    films: List[str]
    species: List[str]
    starships: List[str]
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
        conn.commit()


def _load_cached_characters() -> List[dict]:
    if not DB_PATH.exists():
        return []
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT payload FROM characters").fetchall()
    return [json.loads(row[0]) for row in rows]


def _replace_cache(characters: List[dict]) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM characters")
        conn.executemany(
            "INSERT INTO characters (name, payload) VALUES (?, ?)",
            [(char["name"], json.dumps(char)) for char in characters],
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
        return cached

    raw_people = await _fetch_people()
    simplified = [_transform_character(person) for person in raw_people]
    _replace_cache(simplified)
    return simplified


async def _fetch_name(client: httpx.AsyncClient, url: str) -> Optional[str]:
    """Fetch a resource by URL and return its name/title field."""
    try:
        response = await client.get(url)
        response.raise_for_status()
        payload = response.json()
        return payload.get("name") or payload.get("title")
    except Exception:
        return None


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

    async with httpx.AsyncClient(timeout=10) as client:
        tasks = {
            "homeworld": None,
            "films": [],
            "species": [],
            "starships": [],
        }

        if payload.homeworld:
            tasks["homeworld"] = asyncio.create_task(_fetch_name(client, payload.homeworld))

        for key, urls in [
            ("films", payload.films),
            ("species", payload.species),
            ("starships", payload.starships),
        ]:
            tasks[key] = [asyncio.create_task(_fetch_name(client, url)) for url in urls]

        homeworld_name = await tasks["homeworld"] if tasks["homeworld"] else None
        films = [name for name in await asyncio.gather(*tasks["films"])] if tasks["films"] else []
        species = (
            [name for name in await asyncio.gather(*tasks["species"])] if tasks["species"] else []
        )
        starships = (
            [name for name in await asyncio.gather(*tasks["starships"])]
            if tasks["starships"]
            else []
        )

    # Filter out Nones for failed lookups
    return ResolveResponse(
        homeworld=homeworld_name,
        films=[n for n in films if n],
        species=[n for n in species if n],
        starships=[n for n in starships if n],
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    _init_db()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
