import Spinner from './Spinner';
import { formatList, formatMass } from '../helpers/text';

const DetailOverlay = ({ character, details, loading, onClose }) => {
  if (!character) return null;

  return (
    <div className="overlay" role="dialog" aria-modal="true">
      <div className="overlay__card">
        <div className="overlay__header">
          <div>
            <p className="eyebrow">Character dossier</p>
            <h2>{character.name}</h2>
          </div>
          <button className="overlay__close" onClick={onClose}>
            Close
          </button>
        </div>
        <div className="overlay__body">
          <div className="detail-grid">
            <div>
              <h4>Vitals</h4>
              <ul>
                <li>Height (cm): {character.height_cm || 'Unknown'}</li>
                <li>Height (in): {character.height_in || 'Unknown'}</li>
                <li>Mass: {formatMass(character.mass_kg)}</li>
                <li>Birth year: {character.birth_year || 'Unknown'}</li>
                <li>Gender: {character.gender || 'Unknown'}</li>
              </ul>
            </div>
            <div>
              <h4>Appearance</h4>
              <ul>
                <li>Hair color: {character.hair_color || 'Unknown'}</li>
                <li>Eye color: {character.eye_color || 'Unknown'}</li>
              </ul>
            </div>
            {loading ? (
              <div className="detail-loading" style={{ gridColumn: 'span 2' }}>
                <Spinner />
                <p className="loading-copy">Pulling data from distant systems...</p>
              </div>
            ) : (
              <>
                <div>
                  <h4>Origins & travel</h4>
                  <ul>
                    <li>Homeworld: {details?.homeworld || character.homeworld || 'Unknown'}</li>
                    <li>Vehicles: {formatList(details?.vehicles)}</li>
                    <li>Starships: {formatList(details?.starships)}</li>
                  </ul>
                </div>
                <div>
                  <h4>Appearances</h4>
                  <ul>
                    <li>Films: {formatList(details?.films)}</li>
                    <li>Species: {formatList(details?.species)}</li>
                  </ul>
                </div>
              </>
            )}
          </div>
          <div className="link-row">
            {character.url && (
              <a href={character.url} target="_blank" rel="noreferrer">
                View on SWAPI ↗
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DetailOverlay;
