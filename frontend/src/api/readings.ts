export interface Reading {
  id: number;
  device_id: string;
  temperature_c: number;
  humidity_pct: number;
  measured_at: string | null;
  received_at: string;
}

export const DEVICE_ID = "esp32-01";

export async function getReadings(signal: AbortSignal): Promise<Reading[]> {
  const query = new URLSearchParams({ device_id: DEVICE_ID, limit: "100" });
  // History already includes the latest reading, so one request keeps both views consistent.
  const response = await fetch(`/api/readings?${query}`, { signal });
  if (!response.ok) {
    throw new Error(`Readings request failed (HTTP ${response.status}).`);
  }
  return response.json();
}
