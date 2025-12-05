export const formatList = (arr) => {
  if (!arr || arr.length === 0) return 'None';
  return arr.join(', ');
};

export const formatMass = (mass) => {
  if (mass === null || mass === undefined || mass === 'unknown') return 'Unknown';
  return `${mass} kg`;
};
