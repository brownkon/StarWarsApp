export const formatList = (arr) => {
  if (!arr || arr.length === 0) return 'None';
  return arr.join(', ');
};
