import { useEffect, useMemo, useRef, useState } from 'react';
import CharacterCard from './components/CharacterCard';
import DetailOverlay from './components/DetailOverlay';
import InfoBanner from './components/InfoBanner';
import Spinner from './components/Spinner';
import { fetchCharacterDetails, fetchCharacters, SORT_OPTIONS } from './helpers/api';

function App() {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('mass_kg');
  const [order, setOrder] = useState('desc');
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [details, setDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [filters, setFilters] = useState({
    homeworld: '',
    films: [],
    species: '',
    gender: '',
  });
  const [filmDropdownOpen, setFilmDropdownOpen] = useState(false);
  const filmDropdownRef = useRef(null);
  const showInitialLoading = loading && characters.length === 0;

  const setFilter = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const toggleFilm = (film) => {
    setFilters((prev) => {
      const exists = prev.films.includes(film);
      const films = exists ? prev.films.filter((f) => f !== film) : [...prev.films, film];
      return { ...prev, films };
    });
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (filmDropdownRef.current && !filmDropdownRef.current.contains(e.target)) {
        setFilmDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadCharacters = async (forceRefresh = false) => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchCharacters(sortBy, order, forceRefresh);
      setCharacters(data);
    } catch (err) {
      setError(err.message || 'Failed to load characters.');
      setCharacters([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCharacters();
  }, [sortBy, order]);

  const filterOptions = useMemo(() => {
    const homeworlds = new Set();
    const films = new Set();
    const species = new Set();
    const genders = new Set();
    const filmOrder = [
      'The Phantom Menace',
      'Attack of the Clones',
      'Revenge of the Sith',
      'A New Hope',
      'The Empire Strikes Back',
      'Return of the Jedi',
      'The Force Awakens',
    ];

    characters.forEach((c) => {
      const homeworldVal = c.homeworld_name || c.homeworld;
      if (homeworldVal) homeworlds.add(homeworldVal);

      const filmVals =
        (c.film_titles && c.film_titles.length > 0 ? c.film_titles : c.films) || [];
      filmVals.forEach((f) => f && films.add(f));

      const speciesVals =
        (c.species_names && c.species_names.length > 0 ? c.species_names : c.species) || [];
      speciesVals.forEach((s) => s && species.add(s));

      if (c.gender) genders.add(c.gender);
    });

    const sortAlpha = (arr) => arr.sort((a, b) => a.localeCompare(b));
    const sortFilms = (arr) =>
      arr.sort((a, b) => {
        const ai = filmOrder.indexOf(a);
        const bi = filmOrder.indexOf(b);
        if (ai === -1 && bi === -1) return a.localeCompare(b);
        if (ai === -1) return 1;
        if (bi === -1) return -1;
        return ai - bi;
      });

    return {
      homeworlds: sortAlpha(Array.from(homeworlds)),
      films: sortFilms(Array.from(films)),
      species: sortAlpha(Array.from(species)),
      genders: Array.from(genders),
    };
  }, [characters]);

  const filteredCharacters = useMemo(() => {
    const term = search.trim().toLowerCase();
    return characters.filter((character) => {
      if (term && !character.name.toLowerCase().includes(term)) return false;
      const homeworldVal = character.homeworld_name || character.homeworld;
      const filmVals =
        (character.film_titles && character.film_titles.length > 0
          ? character.film_titles
          : character.films) || [];
      const speciesVals =
        (character.species_names && character.species_names.length > 0
          ? character.species_names
          : character.species) || [];

      if (filters.homeworld && homeworldVal !== filters.homeworld) return false;
      if (filters.films.length > 0 && !filters.films.some((f) => filmVals.includes(f))) {
        return false;
      }
      if (filters.species && !speciesVals.includes(filters.species)) return false;
      if (filters.gender && character.gender !== filters.gender) return false;
      return true;
    });
  }, [characters, filters, search]);

  useEffect(() => {
    if (!selectedCharacter) {
      setDetails(null);
      setDetailsLoading(false);
      return;
    }

    const needsResolve = () => {
      const homeworldNeeds = !!selectedCharacter.homeworld && !selectedCharacter.homeworld_name;
      const filmsNeed =
        (selectedCharacter.films?.length || 0) > (selectedCharacter.film_titles?.length || 0);
      const speciesNeed =
        (selectedCharacter.species?.length || 0) > (selectedCharacter.species_names?.length || 0);
      const starshipsNeed =
        (selectedCharacter.starships?.length || 0) >
        (selectedCharacter.starship_names?.length || 0);
      return homeworldNeeds || filmsNeed || speciesNeed || starshipsNeed;
    };

    if (!needsResolve()) {
      setDetails(null);
      setDetailsLoading(false);
      return;
    }

    const fetchDetails = async () => {
      setDetailsLoading(true);
      try {
        const data = await fetchCharacterDetails(selectedCharacter);
        setDetails(data);
      } catch (err) {
        setDetails({
          homeworld: 'Unavailable',
          films: [],
          species: [],
          starships: [],
          error: err.message,
        });
      } finally {
        setDetailsLoading(false);
      }
    };

    fetchDetails();
  }, [selectedCharacter]);

  return (
    <div className="app-shell">
      <div className="backdrop" />
      <main className="content">
        <header className="hero">
          <div>
            <p className="eyebrow">Full-stack vertical slice</p>
            <h1>Star Wars Data Explorer</h1>
            <p className="subtitle">
            </p>
          </div>
          <div className="cta-row">
            <div className="filter-group">
              <label htmlFor="search">Search by name</label>
              <input
                id="search"
                type="search"
                placeholder="Search..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="filter-group">
              <label htmlFor="sort">Sort by</label>
              <select id="sort" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                {SORT_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="filter-group">
              <label htmlFor="order">Order</label>
              <select id="order" value={order} onChange={(e) => setOrder(e.target.value)}>
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
              </select>
            </div>
            <button className="refresh" onClick={() => loadCharacters(true)} disabled={loading}>
              Refresh
            </button>
          </div>
          <div className="cta-row">
            <div className="filter-group">
              <label htmlFor="homeworld-filter">Homeworld</label>
              <select
                id="homeworld-filter"
                value={filters.homeworld}
                onChange={(e) => setFilter('homeworld', e.target.value)}
              >
                <option value="">All</option>
                {filterOptions.homeworlds.map((world) => (
                  <option key={world} value={world}>
                    {world}
                  </option>
                ))}
              </select>
            </div>
            <div className="filter-group">
              <label htmlFor="film-filter">Movie</label>
              <div
                className="select-dropdown"
                ref={filmDropdownRef}
              >
                <button
                  type="button"
                  className="select-trigger"
                  aria-haspopup="listbox"
                  aria-expanded={filmDropdownOpen}
                  onClick={() => setFilmDropdownOpen((open) => !open)}
                >
                  {filters.films.length === 0
                    ? 'Select movies'
                    : `${filters.films.length} selected`}
                  <span className="chevron">▾</span>
                </button>
                {filmDropdownOpen && (
                  <div id="film-filter" className="select-menu" role="listbox">
                    {filterOptions.films.map((film) => (
                      <label key={film} className="checkbox-item">
                        <input
                          type="checkbox"
                          checked={filters.films.includes(film)}
                          onChange={() => toggleFilm(film)}
                        />
                        <span>{film}</span>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div className="filter-group">
              <label htmlFor="species-filter">Species</label>
              <select
                id="species-filter"
                value={filters.species}
                onChange={(e) => setFilter('species', e.target.value)}
              >
                <option value="">All</option>
                {filterOptions.species.map((spec) => (
                  <option key={spec} value={spec}>
                    {spec}
                  </option>
                ))}
              </select>
            </div>
            <div className="filter-group">
              <label htmlFor="gender-filter">Gender</label>
              <select
                id="gender-filter"
                value={filters.gender}
                onChange={(e) => setFilter('gender', e.target.value)}
              >
                <option value="">All</option>
                {filterOptions.genders.map((g) => (
                  <option key={g} value={g}>
                    {g}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </header>

        {showInitialLoading && (
          <div className="center">
            <Spinner />
            <p className="loading-copy">Loading characters from a galaxy far, far away...</p>
          </div>
        )}

        {!loading && error && (
          <InfoBanner title="Transmission failed" message={error || 'Please try again.'} />
        )}

        {!loading && !error && filteredCharacters.length === 0 && (
          <InfoBanner title="No results" message="No characters match your search." />
        )}

        {!error && filteredCharacters.length > 0 && (
          <section className="grid" aria-live="polite">
            {filteredCharacters.map((character) => (
              <CharacterCard
                key={character.name}
                character={character}
                onSelect={setSelectedCharacter}
              />
            ))}
          </section>
        )}
      </main>

      <DetailOverlay
        character={selectedCharacter}
        details={details}
        loading={detailsLoading}
        onClose={() => setSelectedCharacter(null)}
      />
    </div>
  );
}

export default App;
