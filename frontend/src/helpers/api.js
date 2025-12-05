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
    const message = await response.text();
    throw new Error(message || 'Failed to load characters');
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
    throw new Error('Failed to load details');
  }

  return response.json();
};
