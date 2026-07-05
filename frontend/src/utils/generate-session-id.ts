/**
 * Generate a random session ID for RAG conversation tracking.
 * Uses crypto.randomUUID when available, falls back to a simple random hex string.
 */
export function generateSessionId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  return Array.from({ length: 32 }, () =>
    Math.floor(Math.random() * 16).toString(16),
  ).join('');
}
