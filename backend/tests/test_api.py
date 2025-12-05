import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


transport = ASGITransport(app=app)


@pytest.mark.anyio("asyncio")
async def test_health_endpoint():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.anyio("asyncio")
async def test_characters_sorted_and_enriched(monkeypatch):
    sample = [
        {
            "name": "Heavy",
            "height_cm": 180,
            "height_in": 70.9,
            "mass_kg": 120,
            "birth_year": "10BBY",
            "gender": "male",
            "hair_color": "brown",
            "eye_color": "brown",
            "homeworld": "http://swapi.test/planets/1",
            "homeworld_name": "World A",
            "films": ["http://swapi.test/films/1"],
            "film_titles": ["Film One"],
            "species": ["http://swapi.test/species/1"],
            "species_names": ["Spec One"],
            "starships": ["http://swapi.test/starships/1"],
            "starship_names": ["Ship One"],
            "url": "http://swapi.test/people/1",
        },
        {
            "name": "Light",
            "height_cm": 150,
            "height_in": 59.1,
            "mass_kg": 60,
            "birth_year": "12BBY",
            "gender": "female",
            "hair_color": "black",
            "eye_color": "green",
            "homeworld": "http://swapi.test/planets/2",
            "homeworld_name": "World B",
            "films": ["http://swapi.test/films/2"],
            "film_titles": ["Film Two"],
            "species": ["http://swapi.test/species/2"],
            "species_names": ["Spec Two"],
            "starships": [],
            "starship_names": [],
            "url": "http://swapi.test/people/2",
        },
    ]

    async def fake_source(refresh: bool):
        return sample

    monkeypatch.setattr("app.main._get_characters_from_source", fake_source)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/characters?sort_by=mass_kg&order=desc")

    assert resp.status_code == 200
    data = resp.json()
    assert [c["name"] for c in data] == ["Heavy", "Light"]
    assert data[0]["homeworld_name"] == "World A"
    assert data[0]["film_titles"] == ["Film One"]
    assert data[1]["species_names"] == ["Spec Two"]
