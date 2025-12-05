const CharacterCard = ({ character, onSelect }) => {
  const heightLabel = character.height_cm
    ? `${character.height_cm} cm / ${character.height_in}"`
    : 'Unknown';
  const massLabel = character.mass_kg ? `${character.mass_kg} kg` : 'Unknown';

  return (
    <article
      className="card"
      role="button"
      tabIndex={0}
      onClick={() => onSelect(character)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect(character);
        }
      }}
    >
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

export default CharacterCard;
