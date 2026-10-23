import { useEffect, useState } from "react";
import CapstoneFiles from "./CapstoneFiles";
import { api } from "./api";
import { readLocal, writeLocal, removeLocal, storageKey } from "./storage";
import type { Submission } from "./types";
const measurementFields = [
  ["latency", "Latency: measured value, method and conditions"],
  ["cost", "Cost: measured usage or explicit offline / unmeasured status"],
  ["quality", "Quality: metric, score and dataset size"],
  ["evaluation", "Evaluation: dataset / test revision and observed failures"],
  ["context", "Context: selection, limits, truncation and caching"],
  [
    "limitations",
    "Limitations: deployment, failure recovery and untested claims",
  ],
] as const;
const empty = {
  artifact_url: "",
  commit: "",
  evidence: "",
  measurements: {
    mode: "offline",
    latency: "",
    cost: "",
    quality: "",
    evaluation: "",
    context: "",
    limitations: "",
  } as Record<string, string>,
};
export default function ProjectEvidence({
  lesson,
  programSlug,
}: {
  lesson: number;
  programSlug?: string;
}) {
  const key = storageKey("submission", lesson);
  const [draft, setDraft] = useState(
    () => readLocal<typeof empty>(key) ?? empty,
  );
  const [rows, setRows] = useState<Submission[]>([]);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let alive = true;
    api<Submission[]>(`lessons/${lesson}/submissions/`)
      .then((data) => {
        if (alive) setRows(data);
      })
      .catch((error) => {
        if (alive) setStatus(error.message);
      });
    return () => {
      alive = false;
    };
  }, [lesson]);
  function edit(next: typeof empty) {
    setDraft(next);
    setStatus(
      writeLocal(key, next)
        ? "Draft saved in this browser"
        : "Draft could not be saved locally. Keep this page open.",
    );
  }
  return (
    <section className="evidence-workspace">
      {programSlug && <CapstoneFiles slug={programSlug} />}
      <h2>Submit a project revision</h2>
      <p>
        Keep the checklist as your private practice report. Use this submission
        for a repository or artifact and its engineering evidence. Each
        submission is a new revision, visible to you and staff reviewers.
        Nothing is published automatically. Human review has no guaranteed
        turnaround.
      </p>
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          setBusy(true);
          try {
            const row = await api<Submission>(
              `lessons/${lesson}/submissions/`,
              { method: "POST", body: JSON.stringify(draft) },
            );
            setRows((previous) => [row, ...previous]);
            setDraft(empty);
            removeLocal(key);
            setStatus(
              "Revision submitted for human review. This is not an automatic pass.",
            );
          } catch (error) {
            setStatus((error as Error).message);
          } finally {
            setBusy(false);
          }
        }}
      >
        <label>
          Artifact or repository URL
          <input
            disabled={busy}
            aria-label="Artifact or repository URL"
            type="url"
            required
            maxLength={1000}
            value={draft.artifact_url}
            onChange={(e) => edit({ ...draft, artifact_url: e.target.value })}
            placeholder="https://…"
          />
        </label>
        <label>
          Commit or release identifier
          <input
            disabled={busy}
            aria-label="Commit or release identifier"
            maxLength={80}
            value={draft.commit}
            onChange={(e) => edit({ ...draft, commit: e.target.value })}
          />
        </label>
        <label>
          Evidence and reproduction steps
          <textarea
            disabled={busy}
            required
            aria-label="Evidence and reproduction steps"
            minLength={80}
            maxLength={12000}
            rows={5}
            value={draft.evidence}
            onChange={(e) => edit({ ...draft, evidence: e.target.value })}
          />
        </label>
        <label>
          Measurement environment
          <select
            disabled={busy}
            aria-label="Measurement environment"
            value={draft.measurements.mode}
            onChange={(e) =>
              edit({
                ...draft,
                measurements: { ...draft.measurements, mode: e.target.value },
              })
            }
          >
            <option value="offline">Offline / scripted provider</option>
            <option value="live">Live provider</option>
            <option value="mixed">
              Mixed: describe which measurements are live
            </option>
          </select>
        </label>
        {measurementFields.map(([id, label]) => (
          <label key={id}>
            {label}
            <textarea
            disabled={busy}
              required
              aria-label={label}
              rows={2}
              maxLength={2000}
              value={draft.measurements[id]}
              onChange={(e) =>
                edit({
                  ...draft,
                  measurements: { ...draft.measurements, [id]: e.target.value },
                })
              }
            />
          </label>
        ))}
        <button className="button" disabled={busy}>
          {busy ? "Submitting…" : "Submit project revision"}
        </button>
      </form>
      <p role="status">{status}</p>
      <h3>Your submitted revisions</h3>
      {rows.length === 0 ? (
        <p>No project revisions submitted for this lesson.</p>
      ) : (
        rows.map((row) => (
          <details className="submission-row" key={row.id}>
            <summary>
              Revision #{row.id} · {row.review_status.replaceAll("_", " ")} ·{" "}
              {new Date(row.created_at).toLocaleDateString()}
            </summary>
            <p>
              <a href={row.artifact_url} target="_blank" rel="noreferrer">
                Open submitted artifact
              </a>{" "}
              · {row.commit || "No commit specified"}
            </p>
            <pre>{row.evidence}</pre>
            <dl>
              {Object.entries(row.measurements).map(([name, value]) => (
                <div key={name}>
                  <dt>{name}</dt>
                  <dd>{value}</dd>
                </div>
              ))}
            </dl>
            {row.review_feedback && (
              <div className="quiz-feedback">
                <strong>Review by {row.reviewer}</strong>
                <p>{row.review_feedback}</p>
              </div>
            )}
            <button
              className="text-button"
              onClick={() => {
                const url = URL.createObjectURL(
                  new Blob([JSON.stringify(row, null, 2)], {
                    type: "application/json",
                  }),
                );
                const a = document.createElement("a");
                a.href = url;
                a.download = `project-evidence-${row.id}.json`;
                a.click();
                URL.revokeObjectURL(url);
              }}
            >
              Export evidence report
            </button>
          </details>
        ))
      )}
    </section>
  );
}
