import { useEffect, useMemo, useState } from 'react';
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

  const loadCharacters = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchCharacters(sortBy, order);
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

  const filteredCharacters = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return characters;
    return characters.filter((character) => character.name.toLowerCase().includes(term));
  }, [characters, search]);

  useEffect(() => {
    if (!selectedCharacter) {
      setDetails(null);
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
          vehicles: [],
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
            <button className="refresh" onClick={loadCharacters} disabled={loading}>
              Refresh
            </button>
          </div>
        </header>

        {loading && (
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

        {!loading && !error && filteredCharacters.length > 0 && (
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
