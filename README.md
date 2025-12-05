# Development Process

I chose a full stack focus (Option C) with the Star Wars API.

I leveraged quite a bit AI (I used Codex in VS Code). I first gave it the instructions given with Option C and the Star Wars API and asked for a requirement document. I looked over this and edited it to include other features I wanted and removed some that were unnecessary.

I then created another chat and gave the requirement doc to the model. It gave a very good base project and I spent the next two hours or so iterating through with the model. It did a very good job of inacting my instructions as I went feature by feature. While waiting for the model I looked through the site and saw any bugs or missing features. I also made sure to use git branches and push frecuently as AI has a habit of messing projects up. 

With every response from the model I read the code to make sure it was fine. One time when trying to make the selections of the movies the model had trouble so I did step in and code this manually. 

Once I got a product I was satisfied with I went through the Readme and requirements documents to update them. I really enjoyed working on it and I look forward to similar projects in the future. 

# Star Wars Data Explorer

A lightweight full-stack vertical slice that fetches characters from the Star Wars API (SWAPI) via a FastAPI backend and displays them in a React frontend with filtering, sorting, and detail overlays.

## Stack
- Backend: FastAPI, httpx, SQLite cache
- Frontend: React (Vite), fetch API
- Source API: https://swapi.dev

## Run locally (quick start)
1) Backend: create/activate a venv, install deps, then start uvicorn:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The SQLite file `backend/app/swapi_cache.db` is created automatically and caches SWAPI characters plus resolved names (homeworlds, films, species, starships) to avoid repeat network calls. This is to avoid excess API calls and speed up the user experience. Delete the file or call `/api/characters?refresh=true` to fully repopulate. 

2) Frontend: in a new terminal run Vite dev server (proxies `/api` to the backend on port 8000):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open the printed localhost URL (default http://localhost:5173).

## Backend

### Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### Run
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Test
```bash
cd backend
pytest
```

### Data/cache
- SQLite is used only as a local cache (`app/swapi_cache.db`) so repeated requests do not keep hitting SWAPI. It stores:
  - characters payloads returned by `/api/characters`
  - resolved name/title values for `/api/resolve`
- No manual setup is required; the file is created on startup if missing.

### Example requests
```bash
curl "http://localhost:8000/api/characters?sort_by=mass_kg&order=desc"

curl -X POST "http://localhost:8000/api/resolve" \
  -H "Content-Type: application/json" \
  -d '{
        "homeworld": "https://swapi.dev/api/planets/1/",
        "films": ["https://swapi.dev/api/films/1/"],
        "species": [],
        "starships": []
      }'
```

## Frontend

### Setup & Run
```bash
cd frontend
npm install
npm run dev -- --host --port 5173
```

## Development notes
- `/api/characters` fetches, transforms, sorts, and caches SWAPI people with resolved display names.
- `/api/resolve` resolves URLs to names (homeworld, films, species, starships) with caching.
- Error handling: network/HTTP/invalid-payload issues from SWAPI return 5xx with helpful detail; the frontend surfaces these messages in its banners/overlays.
