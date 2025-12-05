const Spinner = () => (
  <div className="spinner" aria-label="loading">
    <div className="spinner__core" />
    <div className="spinner__ring spinner__ring--outer" />
    <div className="spinner__ring spinner__ring--inner" />
    <div className="spinner__orbit">
      <span />
      <span />
      <span />
    </div>
  </div>
);

export default Spinner;
