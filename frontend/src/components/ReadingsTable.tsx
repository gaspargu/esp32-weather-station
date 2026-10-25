import type { Reading } from "../api/readings";
import { formatDate } from "../format";

export default function ReadingsTable({ readings }: { readings: Reading[] }) {
  return (
    <section aria-labelledby="history-title" className="history">
      <div className="section-heading">
        <h2 id="history-title">Recent readings</h2>
        <span>Latest {readings.length} · newest first</span>
      </div>
      <div className="table-scroll" role="region" aria-label="Recent readings table" tabIndex={0}>
        <table>
          <thead>
            <tr>
              <th scope="col">Received at</th>
              <th scope="col">Measured at</th>
              <th scope="col" className="numeric">Temperature</th>
              <th scope="col" className="numeric">Humidity</th>
            </tr>
          </thead>
          <tbody>
            {readings.map((reading) => (
              <tr key={reading.id}>
                <td>{formatDate(reading.received_at)}</td>
                <td>{formatDate(reading.measured_at)}</td>
                <td className="numeric">{reading.temperature_c.toFixed(1)} °C</td>
                <td className="numeric">{reading.humidity_pct.toFixed(1)} %</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
