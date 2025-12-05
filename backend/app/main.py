"""FastAPI backend for the Star Wars Data Explorer vertical slice."""
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

SWAPI_PEOPLE_URL = "https://swapi.dev/api/people/"

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
    }


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


@app.get("/api/characters", response_model=List[Character])
async def list_characters(
    sort_by: str = Query(
        "mass_kg", enum=["name", "height_cm", "mass_kg"], description="Server-side sort field"
    ),
    order: str = Query("desc", enum=["asc", "desc"], description="Sort order"),
):
    """Fetch characters from SWAPI, simplify the shape, and sort before returning."""

    raw_people = await _fetch_people()
    simplified = [_transform_character(person) for person in raw_people]

    reverse = order == "desc"
    simplified.sort(key=_sorting_key(sort_by), reverse=reverse)
    return simplified


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
