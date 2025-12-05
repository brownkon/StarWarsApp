import httpx
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


@pytest.mark.anyio("asyncio")
async def test_characters_swapi_http_error(monkeypatch):
    request = httpx.Request("GET", "https://swapi.dev/api/people/")

    class FakeResponse:
        def __init__(self):
            self.response = httpx.Response(500, request=request)

        def raise_for_status(self):
            raise httpx.HTTPStatusError("boom", request=request, response=self.response)

        def json(self):
            return {}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            return FakeResponse()

    monkeypatch.setattr("app.main.httpx.AsyncClient", FakeClient)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/characters?refresh=true")

    assert resp.status_code == 502
    assert "SWAPI returned an error" in resp.json()["detail"]


@pytest.mark.anyio("asyncio")
async def test_resolve_swapi_network_error(monkeypatch):
    class FailingClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            raise httpx.RequestError("network down", request=httpx.Request("GET", url))

    monkeypatch.setattr("app.main.httpx.AsyncClient", FailingClient)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/api/resolve",
            json={"homeworld": "https://swapi.dev/api/planets/1"},
        )

    assert resp.status_code == 504
    assert "Unable to reach SWAPI" in resp.json()["detail"]
