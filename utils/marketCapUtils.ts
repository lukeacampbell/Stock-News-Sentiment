
export const parseMarketCap = (capStr: string): number => {
  if (!capStr) return 0;
  const upperCapStr = capStr.toUpperCase();
  const value = parseFloat(upperCapStr.replace(/[^0-9.]/g, ''));

  if (isNaN(value)) return 0;

  if (upperCapStr.includes('T')) {
    return value * 1e12;
  }
  if (upperCapStr.includes('B')) {
    return value * 1e9;
  }
  if (upperCapStr.includes('M')) {
    return value * 1e6;
  }
  return value;
};
