import type { Reading } from "../api/readings";
import { formatDate } from "../format";

export default function DeviceCard({ reading, now }: { reading: Reading; now: number }) {
  const stale = now - new Date(reading.received_at).getTime() >= 90_000;

  return (
    <section className="device-card" aria-labelledby="device-title">
      <div className="device-heading">
        <div>
          <p className="label">Device</p>
          <h2 id="device-title">{reading.device_id}</h2>
        </div>
        <span className={`status ${stale ? "stale" : "fresh"}`}>
          <span aria-hidden="true">●</span> {stale ? "Stale" : "Fresh"}
        </span>
      </div>
      <dl className="measurements">
        <div className="temperature">
          <dt>Temperature</dt>
          <dd>{reading.temperature_c.toFixed(1)}<span> °C</span></dd>
        </div>
        <div className="humidity">
          <dt>Humidity</dt>
          <dd>{reading.humidity_pct.toFixed(1)}<span> %</span></dd>
        </div>
      </dl>
      <dl className="timestamps">
        <div><dt>Measured at</dt><dd>{formatDate(reading.measured_at)}</dd></div>
        <div><dt>Received at</dt><dd>{formatDate(reading.received_at)}</dd></div>
      </dl>
      {stale && <p className="stale-note">No new readings received in the last 90 seconds.</p>}
    </section>
  );
}
