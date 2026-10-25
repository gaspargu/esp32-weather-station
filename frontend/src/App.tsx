import { useCallback, useEffect, useRef, useState } from "react";
import { DEVICE_ID, getReadings, type Reading } from "./api/readings";
import DeviceCard from "./components/DeviceCard";
import ReadingsTable from "./components/ReadingsTable";
import { timeZone } from "./format";

export default function App() {
  const [readings, setReadings] = useState<Reading[]>([]);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [now, setNow] = useState(Date.now());
  const request = useRef<AbortController | null>(null);

  const refresh = useCallback(async () => {
    if (request.current) return;
    const controller = new AbortController();
    request.current = controller;
    setLoading(true);
    // Bound requests so an unreachable API cannot block future refreshes indefinitely.
    const timeout = window.setTimeout(() => controller.abort(), 10_000);
    try {
      const result = await getReadings(controller.signal);
      if (request.current !== controller) return;
      setReadings(result);
      setHasLoaded(true);
      setError(false);
      setNow(Date.now());
    } catch {
      if (request.current === controller) setError(true);
    } finally {
      window.clearTimeout(timeout);
      if (request.current === controller) {
        request.current = null;
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    void refresh();
    const polling = window.setInterval(() => void refresh(), 30_000);
    const clock = window.setInterval(() => setNow(Date.now()), 1_000);
    return () => {
      window.clearInterval(polling);
      window.clearInterval(clock);
      const activeRequest = request.current;
      request.current = null;
      activeRequest?.abort();
    };
  }, [refresh]);

  const latest = readings[0];

  return (
    <main>
      <header className="page-heading">
        <div>
          <p className="label">Environmental monitor</p>
          <h1>Weather station</h1>
          <p className="subtitle">Temperature & humidity · DHT22</p>
        </div>
        <button onClick={() => void refresh()} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </header>

      <div aria-live="polite" role="status" className="update-status">
        {error && (
          <p className="error">Could not refresh readings. {hasLoaded ? "Showing last available data. " : ""}
            Check the API connection and try Refresh. Automatic retry every 30 seconds.
          </p>
        )}
        {!hasLoaded && loading && <p>Loading readings…</p>}
      </div>

      {latest ? (
        <>
          <DeviceCard reading={latest} now={now} />
          <ReadingsTable readings={readings} />
        </>
      ) : hasLoaded ? (
        <section className="empty">
          <h2>No readings yet</h2>
          <p>Waiting for data from <strong>{DEVICE_ID}</strong>. New readings will appear automatically.</p>
        </section>
      ) : null}

      <footer>
        <span>Updates every 30 seconds</span>
        <span>Dates shown in {timeZone}. Measured time is provided by the device; received time by the server.</span>
      </footer>
    </main>
  );
}
