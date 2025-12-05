export const SORT_OPTIONS = [
  { value: 'mass_kg', label: 'Mass' },
  { value: 'height_cm', label: 'Height' },
  { value: 'name', label: 'Name' },
  { value: 'birth_year', label: 'Birth Year' },
];

export const fetchCharacters = async (sortBy, order, refresh = false) => {
  const params = new URLSearchParams({ sort_by: sortBy, order });
  if (refresh) params.append('refresh', 'true');
  const response = await fetch(`/api/characters?${params.toString()}`);
  if (!response.ok) {
    let message = 'Failed to load characters';
    try {
      const body = await response.json();
      message = body.detail || body.message || message;
    } catch {
      const text = await response.text();
      if (text) message = text;
    }
    throw new Error(message);
  }
  return response.json();
};

export const fetchCharacterDetails = async (character) => {
  const response = await fetch('/api/resolve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      homeworld: character.homeworld,
      films: character.films || [],
      species: character.species || [],
      starships: character.starships || [],
    }),
  });

  if (!response.ok) {
    let message = 'Failed to load details';
    try {
      const body = await response.json();
      message = body.detail || body.message || message;
    } catch {
      const text = await response.text();
      if (text) message = text;
    }
    throw new Error(message);
  }

  return response.json();
};
