import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import type { Reading } from "./api/readings";
import { formatDate } from "./format";

const reading: Reading = {
  id: 1,
  device_id: "esp32-01",
  temperature_c: 24.3,
  humidity_pct: 58.2,
  measured_at: null,
  received_at: "2026-10-25T12:00:00Z",
};

function respond(data: Reading[]) {
  return { ok: true, json: async () => data } as Response;
}

const fetchMock = vi.fn<typeof fetch>();

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date(reading.received_at));
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

async function openDashboard() {
  await act(async () => { render(<App />); });
}

describe("Dashboard", () => {
  it("shows device, values, reception time, and absent measurement time", async () => {
    fetchMock.mockResolvedValue(respond([reading]));
    await openDashboard();
    const card = screen.getByRole("region", { name: "esp32-01" });
    expect(within(card).getByText("24.3")).toBeInTheDocument();
    expect(within(card).getByText("58.2")).toBeInTheDocument();
    expect(within(card).getByText("Not provided")).toBeInTheDocument();
    expect(within(card).getByText(formatDate(reading.received_at), { normalizer: (text) => text })).toBeInTheDocument();
    expect(within(card).getByText(/Fresh/)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/readings?device_id=esp32-01&limit=100", { signal: expect.any(AbortSignal) },
    );
  });

  it("shows a device measurement timestamp when supplied", async () => {
    const measured = "2026-10-25T11:59:55Z";
    fetchMock.mockResolvedValue(respond([{ ...reading, measured_at: measured }]));
    await openDashboard();
    const card = screen.getByRole("region", { name: "esp32-01" });
    expect(within(card).getByText(formatDate(measured), { normalizer: (text) => text })).toBeInTheDocument();
  });

  it("shows loading followed by an empty state", async () => {
    let resolve!: (value: Response) => void;
    fetchMock.mockImplementation(() => new Promise((done) => { resolve = done; }));
    render(<App />);
    expect(screen.getByText("Loading readings…")).toBeInTheDocument();
    await act(async () => resolve(respond([])));
    expect(screen.getByText("No readings yet")).toBeInTheDocument();
    expect(screen.queryByText(/Could not refresh/)).not.toBeInTheDocument();
  });

  it("reports network errors and recovers through manual refresh", async () => {
    fetchMock.mockRejectedValueOnce(new Error("Network unavailable"));
    fetchMock.mockResolvedValue(respond([reading]));
    await openDashboard();
    expect(screen.getByRole("status")).toHaveTextContent("Could not refresh readings");
    await act(async () => fireEvent.click(screen.getByRole("button", { name: "Refresh" })));
    expect(screen.getByRole("region", { name: "esp32-01" })).toBeInTheDocument();
    expect(screen.queryByText(/Could not refresh/)).not.toBeInTheDocument();
  });

  it("preserves readings after an HTTP error and recovers on the next poll", async () => {
    fetchMock.mockResolvedValueOnce(respond([reading]));
    fetchMock.mockResolvedValueOnce({ ok: false, status: 503 } as Response);
    fetchMock.mockResolvedValue(respond([{ ...reading, temperature_c: 25.1 }]));
    await openDashboard();
    await act(async () => vi.advanceTimersByTime(30_000));
    expect(screen.getByText("24.3")).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("Showing last available data");
    await act(async () => vi.advanceTimersByTime(30_000));
    expect(screen.getByText("25.1")).toBeInTheDocument();
    expect(screen.queryByText(/Could not refresh/)).not.toBeInTheDocument();
  });

  it("marks readings stale after 90 seconds even if the API is reachable", async () => {
    fetchMock.mockResolvedValue(respond([reading]));
    await openDashboard();
    await act(async () => vi.advanceTimersByTime(90_000));
    expect(screen.getByText(/Stale/)).toBeInTheDocument();
    expect(screen.getByText(/No new readings received/)).toBeInTheDocument();
  });

  it("prevents overlapping requests and aborts an unfinished request on unmount", async () => {
    fetchMock.mockImplementation(() => new Promise(() => {}));
    const view = render(<App />);
    await act(async () => vi.advanceTimersByTime(30_000));
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(screen.getByRole("button")).toBeDisabled();
    const signal = fetchMock.mock.calls[0][1]?.signal;
    view.unmount();
    expect(signal?.aborted).toBe(true);
  });

  it("times out a hanging request and allows the next scheduled retry", async () => {
    fetchMock.mockImplementationOnce((_url, options) => new Promise((_resolve, reject) => {
      options?.signal?.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")));
    }));
    fetchMock.mockResolvedValue(respond([reading]));
    await openDashboard();
    await act(async () => vi.advanceTimersByTime(10_000));
    expect(screen.getByRole("status")).toHaveTextContent("Could not refresh readings");
    expect(screen.getByRole("button", { name: "Refresh" })).toBeEnabled();
    await act(async () => vi.advanceTimersByTime(20_000));
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(screen.getByText("24.3")).toBeInTheDocument();
  });
});
