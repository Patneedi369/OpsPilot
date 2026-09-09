export function formatTimer(totalSeconds: number): string {
  const hours = String(Math.floor(totalSeconds / 3600)).padStart(2, '0');
  const minutes = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0');
  const seconds = String(totalSeconds % 60).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
}

export function padLogLevel(level: string): string {
  return level.padEnd(5, ' ');
}

export function utcNowLabel(): string {
  return new Date().toISOString().slice(11, 19);
}
