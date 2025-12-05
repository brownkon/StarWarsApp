import { useEffect, useMemo, useState } from 'react';

const SORT_OPTIONS = [
  { value: 'mass_kg', label: 'Mass' },
  { value: 'height_cm', label: 'Height' },
  { value: 'name', label: 'Name' },
];

const fetchCharacters = async (sortBy, order) => {
  const params = new URLSearchParams({ sort_by: sortBy, order });
  const response = await fetch(`/api/characters?${params.toString()}`);
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || 'Failed to load characters');
  }
  return response.json();
};

const Spinner = () => (
  <div className="spinner" aria-label="loading">
    <div className="beam" />
    <div className="beam" />
  </div>
);

const InfoBanner = ({ title, message }) => (
  <div className="info-banner">
    <h3>{title}</h3>
    <p>{message}</p>
  </div>
);

const CharacterCard = ({ character }) => {
  const heightLabel = character.height_cm
    ? `${character.height_cm} cm / ${character.height_in}\"`
    : 'Unknown';
  const massLabel = character.mass_kg ? `${character.mass_kg} kg` : 'Unknown';

  return (
    <article className="card">
      <header className="card-title">{character.name}</header>
      <dl>
        <div className="row">
          <dt>Height</dt>
          <dd>{heightLabel}</dd>
        </div>
        <div className="row">
          <dt>Mass</dt>
          <dd>{massLabel}</dd>
        </div>
        <div className="row">
          <dt>Birth year</dt>
          <dd>{character.birth_year || 'Unknown'}</dd>
        </div>
        <div className="row">
          <dt>Gender</dt>
          <dd>{character.gender || 'Unknown'}</dd>
        </div>
      </dl>
    </article>
  );
};

function App() {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('mass_kg');
  const [order, setOrder] = useState('desc');

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
              <CharacterCard key={character.name} character={character} />
            ))}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
