/**
 * Text and data formatting utilities.
 */

/** Capitalize the first letter of a string. */
export function capitalize(str: string): string {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/** Truncate a string to a maximum length with ellipsis. */
export function truncate(str: string, maxLength: number): string {
  if (!str || str.length <= maxLength) return str;
  return `${str.slice(0, maxLength).trimEnd()}…`;
}

/** Format a confidence score (0–1) as a percentage string. */
export function formatConfidence(score: number): string {
  return `${Math.round(score * 100)}%`;
}

/** Convert an array of strings into a comma-separated readable list. */
export function toReadableList(items: string[]): string {
  if (items.length === 0) return '';
  if (items.length === 1) return items[0];
  if (items.length === 2) return `${items[0]} & ${items[1]}`;
  return `${items.slice(0, -1).join(', ')} & ${items[items.length - 1]}`;
}
