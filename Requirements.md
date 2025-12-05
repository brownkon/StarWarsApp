Full-Stack Star Wars Data Explorer – Requirements Document
====================================================

1. Overview
-----------
The goal of this project is to build a minimal, functional full-stack application that acts as a vertical slice:
- A backend service that fetches and transforms data from the Star Wars API (SWAPI: https://swapi.dev/)
- A frontend interface that calls the backend (not SWAPI directly) to display the processed data.

The project intentionally keeps scope small while demonstrating good engineering practices, readability, and thoughtful design choices.

2. Tech Stack
-------------

- Backend: Python FastAPI
- Frontend: React
- API Source: Star Wars API (SWAPI) – https://swapi.dev/
  - Documentation: https://swapi.dev/documentation

3. Functional Requirements
--------------------------

3.1 Backend Requirements
- Provide custom endpoints: `/api/characters` and `/api/resolve`.
- Fetch data from SWAPI (`https://swapi.dev/api/people/`) and paginate all pages.
- Transform/clean the response data:
  - Remove unused fields; keep simplified structure with:
    - `name`, `height_cm`, `height_in`, `mass_kg`, `birth_year`, `gender`, `hair_color`, `eye_color`
    - raw URLs for `homeworld`, `films`, `species`, `starships`
    - resolved display names for `homeworld_name`, `film_titles`, `species_names`, `starship_names`
- Server-side logic:
  - Height conversion cm → inches, server-side sorting (name, height, mass, birth year).
  - SQLite cache for characters and resolved names; `refresh=true` query forces refetch + cache repopulation.
- Return simplified JSON tailored for the frontend; `/api/resolve` resolves SWAPI URLs to names with caching.
- Include example `curl` usage in the README (kept up to date).

3.2 Frontend Requirements
- Call backend endpoints only (`/api/characters`, `/api/resolve`), never SWAPI directly.
- Display transformed Star Wars data in a responsive card grid with search, filtering, and sorting.
- Show Star Wars–themed loading states (page + detail overlay), graceful error and empty states.
- Filters:
  - Name search
  - Homeworld (names), Species (names), Gender
  - Movies: multi-select dropdown by title
- Sorting options: name, height, mass, birth year (asc/desc).
- UI is Star Wars themed and responsive (desktop + mobile).

4. Non-Functional Requirements
------------------------------
- Readable, consistently formatted code; organized backend/frontend structure.
- Clear setup/run instructions in `README.md`.
- Reliability:
  - Handle SWAPI/network failures with 5xx + frontend error messaging.
  - Handle empty states and slow responses with loading placeholders.
  - Use SQLite caching to reduce repeated SWAPI calls; force refresh available via query param/button.

5. User Stories
---------------
As a **user**:
- I want to view a list of Star Wars characters retrieved from a backend service.
- I want the interface to tell me when data is loading, so I know something is happening.
- I want to see basic details about each character without being overwhelmed by unnecessary data.
- I want the interface to look reasonable on both desktop and mobile devices.

As a **reviewer**:
- I want to quickly understand how the backend fetches and transforms data from SWAPI.
- I want to see how the frontend communicates with the backend and handles loading and errors.
- I want to be able to run the project locally with minimal setup steps.
- I want to see a clear explanation of what was implemented and what would be done next with more time.

6. Project Deliverables
-----------------------
- A working backend service that:
  - Fetches data from SWAPI.
  - Transforms and returns a simplified JSON response.
- A working frontend application that:
  - Calls the backend endpoint.
  - Displays the Star Wars data with loading and error states.
- A `README.md` that includes:
  - The chosen track: **Full-Stack** using the **Star Wars API**.
  - Instructions to install dependencies and run both backend and frontend locally.
  - A brief description of the data transformation and server-side logic implemented.
  - Optional: Notes on what you would do next if you had more than 2–3 hours.
  - A short section describing how AI tools (if any) were used during development.

7. Future Enhancements (Optional / Out of Scope)
------------------------------------------------
These are not required for the initial submission but can be mentioned as potential next steps:
- Character detail pages showing additional information (homeworld, films, species, etc.).
- Caching SWAPI responses on the server to reduce external API calls.
- Adding pagination or infinite scroll on the frontend.
- Adding search and advanced filtering (by gender, mass range, etc.).
- Converting the project to TypeScript on both frontend and backend.
- Deploying the app (e.g., backend on Render/Railway and frontend on Vercel) and documenting the deployment process.
