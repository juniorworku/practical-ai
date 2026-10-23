import { useEffect, useState } from "react";
import { api } from "./api";
type Session = {
  id: number;
  title: string;
  program: string;
  starts_at: string;
  ends_at: string;
  places_left: number;
  reserved: boolean;
  meeting_url: string | null;
};
export default function LiveSessions() {
  const [rows, setRows] = useState<Session[]>([]);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let alive = true;
    api<Session[]>("sessions/")
      .then((data) => {
        if (alive) setRows(data);
      })
      .catch((error) => {
        if (alive) setStatus(error.message);
      });
    return () => {
      alive = false;
    };
  }, []);
  return (
    <details className="panel">
      <summary>
        Optional live practice sessions · {rows.length} scheduled
      </summary>
      <p>
        Your programs remain self-paced. Staff can schedule office hours and
        project demos here; only actual scheduled sessions are listed. Times use
        your browser’s local timezone.
      </p>
      {rows.length ? (
        rows.map((row) => (
          <article key={row.id} className="submission-row">
            <h3>{row.title}</h3>
            <p>
              {row.program} · {new Date(row.starts_at).toLocaleString()} –{" "}
              {new Date(row.ends_at).toLocaleTimeString()}
            </p>
            <p>{row.places_left} places available</p>
            <button
              className="text-button"
              disabled={busy || (!row.reserved && !row.places_left)}
              onClick={async () => {
                setBusy(true);
                try {
                  await api(`sessions/${row.id}/reservation/`, {
                    method: row.reserved ? "DELETE" : "POST",
                  });
                  setRows(await api<Session[]>("sessions/"));
                  setStatus(
                    row.reserved
                      ? "Reservation cancelled."
                      : "Your place is reserved.",
                  );
                } catch (error) {
                  setStatus((error as Error).message);
                } finally {
                  setBusy(false);
                }
              }}
            >
              {row.reserved ? "Cancel reservation" : "Reserve a free place"}
            </button>
            {row.meeting_url && (
              <a href={row.meeting_url} target="_blank" rel="noreferrer">
                Open session meeting
              </a>
            )}
          </article>
        ))
      ) : (
        <p>No sessions are currently scheduled for your enrolled programs.</p>
      )}
      <p role="status">{status}</p>
    </details>
  );
}
