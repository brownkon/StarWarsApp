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
- Provide at least one custom endpoint, e.g., `/api/characters`.
- Fetch data from SWAPI (for example, from `https://swapi.dev/api/people/`).
- Transform/clean the response data:
  - Remove unused or overly verbose fields.
  - Keep a simplified structure with essential fields such as:
    - `name`
    - `height`
    - `mass`
    - `birth_year`
    - `gender`
- Implement at least one piece of server-side logic before returning the response, such as:
  - Sorting characters by mass or height.
  - Converting height from centimeters to inches.
- Return a simplified JSON payload tailored to what the frontend needs.
- Include a simple way to test the endpoint:
  - Example `curl` command in the README

3.2 Frontend Requirements
- The frontend must call the **custom backend endpoint** (e.g., `/api/characters`) and not SWAPI directly.
- Display the transformed Star Wars data returned by the backend in a clean layout (cards, list, or grid).
- Include a visible loading state while data is being fetched (Star Wars themed spinner).
- Handle and display error states gracefully (e.g., “Failed to load characters. Please try again.”).
- Use a responsive layout that works on desktop and mobile screen sizes.
- Provide a simple search or filter (e.g., filter by name).
- Provide sorting options in the UI (e.g., sort by name, height, or mass).
- UI that is clean and Star Wars themed.

4. Non-Functional Requirements
------------------------------
- Code should be readable, consistently formatted, and reasonably documented with comments where helpful.
- Project structure should be organized (e.g., clear separation of backend and frontend code).
- Setup and run instructions must be clearly documented in `README.md`.
- The system should handle:
  - Network failures when calling SWAPI (e.g., show an error message on the frontend).
  - Empty states (e.g., if no data is returned or filter yields no results).
  - Slow responses (e.g., keep showing the loading state until data is ready).

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
