import { useEffect, useState } from "react";
import { ArrowUpRight, FolderCheck, GitCommitHorizontal } from "lucide-react";
import { api } from "./api";
type Entry = {
  id: number;
  program: string;
  title: string;
  artifact_url: string;
  commit: string;
  evidence: string;
  measurements: Record<string, string>;
  status: string;
  feedback: string;
  reviewer: string | null;
  created_at: string;
};
export default function StudentPortfolio() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [status, setStatus] = useState("Loading project revisions…");
  const [filter, setFilter] = useState("all");
  useEffect(() => {
    let alive = true;
    api<Entry[]>("portfolio/")
      .then((data) => {
        if (alive) {
          setEntries(data);
          setStatus("");
        }
      })
      .catch((error) => {
        if (alive) setStatus(error.message);
      });
    return () => {
      alive = false;
    };
  }, []);
  const shown = entries.filter(
    (row) => filter === "all" || row.status === filter,
  );
  return (
    <section className="portfolio-page">
      <div className="section-heading">
        <div>
          <span className="eyebrow">BUILD A BODY OF EVIDENCE</span>
          <h1>Your project portfolio</h1>
          <p>
            Revisions, measurements and review feedback. Private until you
            choose to share an exported report.
          </p>
        </div>
        <FolderCheck size={38} />
      </div>
      <div
        className="portfolio-filters"
        role="group"
        aria-label="Filter project revisions"
      >
        {[
          ["all", "All revisions"],
          ["awaiting_review", "Awaiting review"],
          ["changes_requested", "Needs revision"],
          ["reviewed", "Reviewed"],
        ].map(([value, label]) => (
          <button
            className={filter === value ? "selected" : ""}
            aria-pressed={filter === value}
            key={value}
            onClick={() => setFilter(value)}
          >
            {label}
            <span>
              {value === "all"
                ? entries.length
                : entries.filter((row) => row.status === value).length}
            </span>
          </button>
        ))}
      </div>
      {status && <p role="status">{status}</p>}
      {!status && !shown.length && (
        <div className="empty-workspace">
          <FolderCheck size={38} />
          <h2>
            {entries.length
              ? "No revisions match this filter."
              : "Your first project belongs here."}
          </h2>
          <p>
            Open a lesson’s Practical task and submit an artifact with
            reproduction steps and engineering measurements. It will appear here
            with its review status.
          </p>
        </div>
      )}
      <div className="portfolio-grid">
        {shown.map((row) => (
          <article className="surface-card portfolio-entry" key={row.id}>
            <div className="entry-topline">
              <span className="eyebrow">{row.program}</span>
              <span className="status-pill">
                {row.status.replaceAll("_", " ")}
              </span>
            </div>
            <h2>{row.title}</h2>
            <small>
              Revision #{row.id} ·{" "}
              {new Date(row.created_at).toLocaleDateString()}
            </small>
            <p>{row.evidence}</p>
            {row.commit && (
              <small className="commit-label">
                <GitCommitHorizontal size={14} />
                {row.commit}
              </small>
            )}
            <div className="entry-metrics">
              {["mode", "latency", "cost", "quality"].map((key) => (
                <div key={key}>
                  <small>{key}</small>
                  <span>{row.measurements[key]}</span>
                </div>
              ))}
            </div>
            <details>
              <summary>Evaluation, context and limitations</summary>
              {["evaluation", "context", "limitations"].map((key) => (
                <p key={key}>
                  <strong>{key}: </strong>
                  {row.measurements[key]}
                </p>
              ))}
            </details>
            {row.feedback && (
              <div className="review-note">
                <strong>Feedback · {row.reviewer}</strong>
                <p>{row.feedback}</p>
              </div>
            )}
            <div className="entry-actions">
              <a
                className="text-button"
                href={row.artifact_url}
                target="_blank"
                rel="noreferrer"
              >
                Open artifact
                <ArrowUpRight size={15} />
              </a>
              <button
                className="text-button"
                onClick={() => {
                  const url = URL.createObjectURL(
                    new Blob([JSON.stringify(row, null, 2)], {
                      type: "application/json",
                    }),
                  );
                  const link = document.createElement("a");
                  link.href = url;
                  link.download = `project-evidence-${row.id}.json`;
                  link.click();
                  URL.revokeObjectURL(url);
                }}
              >
                Export evidence
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
