import { useEffect, useRef, useState } from "react";
import type { Lab, LabCheck } from "./types";
import { api } from "./api";
import { readLocal, writeLocal, storageKey } from "./storage";
import { TeachingMarkdown } from "./ConceptReader";
export default function BrowserLab({
  lesson,
  lab,
  preview = false,
}: {
  lesson: number;
  lab: Lab;
  preview?: boolean;
}) {
  const key = storageKey("lab-" + lab.revision, lesson);
  const [code, setCode] = useState(() => readLocal<string>(key) ?? lab.starter);
  const [results, setResults] = useState<LabCheck[]>([]);
  const [output, setOutput] = useState("");
  const [status, setStatus] = useState("");
  const [run, setRun] = useState(0);
  const [busy, setBusy] = useState(false);
  const frame = useRef<HTMLIFrameElement>(null);
  const executed = useRef("");
  useEffect(() => {
    if (preview) return;
    let alive = true;
    api<{ latest: { code: string; results: LabCheck[] } | null }>(
      `lessons/${lesson}/lab-attempts/`,
    )
      .then((data) => {
        if (alive && data.latest && !readLocal(key)) {
          setCode(data.latest.code);
          setResults(data.latest.results);
          executed.current = data.latest.code;
          setStatus("Restored your last browser-run attempt");
        }
      })
      .catch((error) => {
        if (alive) setStatus(error.message);
      });
    return () => {
      alive = false;
    };
  }, [lesson, lab.revision, preview, key]);
  useEffect(() => {
    if (!run) return;
    let finished = false;
    const timeout = window.setTimeout(() => {
      finished = true;
      setBusy(false);
      setRun(0);
      setStatus(
        "Stopped after 30 seconds. Check for a loop or retry if the runtime was still loading.",
      );
    }, 30000);
    const receive = async (event: MessageEvent) => {
      if (event.source !== frame.current?.contentWindow || finished) return;
      if (event.data?.type === "ready")
        frame.current?.contentWindow?.postMessage(
          { type: "run", code: executed.current, checks: lab.checks },
          "*",
        );
      if (event.data?.type === "result") {
        finished = true;
        window.clearTimeout(timeout);
        setBusy(false);
        const checks = event.data.results as LabCheck[];
        if (!Array.isArray(checks) || checks.length !== lab.checks.length) {
          setStatus("Runner returned an invalid report. Retry.");
          return;
        }
        setResults(checks);
        setOutput(String(event.data.output || "").slice(0, 12000));
        setStatus(
          checks.every((row) => row.passed)
            ? "All browser checks passed. These check behavior, not factual support."
            : "Some checks failed. Use the feedback below and revise your code.",
        );
        if (!preview) {
          try {
            await api(`lessons/${lesson}/lab-attempts/`, {
              method: "POST",
              body: JSON.stringify({
                revision: lab.revision,
                code: executed.current,
                results: checks,
              }),
            });
            window.dispatchEvent(new Event("academy-progress"));
          } catch (error) {
            setStatus(
              "Results kept here; account sync failed: " +
                (error as Error).message,
            );
          }
        }
      }
      if (event.data?.type === "error") {
        finished = true;
        window.clearTimeout(timeout);
        setBusy(false);
        setStatus(String(event.data.message));
      }
    };
    window.addEventListener("message", receive);
    return () => {
      finished = true;
      window.clearTimeout(timeout);
      window.removeEventListener("message", receive);
    };
  }, [run, lesson, lab, preview]);
  return (
    <section className="browser-lab" aria-label="Python practice lab">
      <span className="eyebrow">EDIT · RUN · INSPECT · REVISE</span>
      <h2>{lab.title}</h2>
      <TeachingMarkdown>{lab.teaching}</TeachingMarkdown>
      <details>
        <summary>The exact checks you will run</summary>
        {lab.checks.map((check) => (
          <div key={check.name}>
            <strong>{check.name}</strong>
            <pre>{check.expression}</pre>
          </div>
        ))}
      </details>
      <label>
        Python solution
        <textarea
          aria-label="Python solution"
          className="code-editor"
          rows={16}
          spellCheck={false}
          autoCapitalize="off"
          maxLength={20000}
          value={code}
          disabled={busy}
          onChange={(event) => {
            setCode(event.target.value);
            writeLocal(key, event.target.value);
            setStatus(
              "Draft saved in this browser. Run again to check this version.",
            );
          }}
        />
      </label>
      <div className="task-actions">
        <button
          className="button"
          disabled={busy}
          onClick={() => {
            executed.current = code;
            setResults([]);
            setOutput("");
            setStatus(
              "Loading the local Python runtime and running your checks…",
            );
            setBusy(true);
            setRun((value) => value + 1);
          }}
        >
          {busy ? "Running…" : "Run tests"}
        </button>
        {busy && (
          <button
            className="text-button"
            onClick={() => {
              setRun(0);
              setBusy(false);
              setStatus("Stopped. Your code draft is retained.");
            }}
          >
            Stop execution
          </button>
        )}
        <button
          className="text-button"
          disabled={busy}
          onClick={() => {
            setCode(lab.starter);
            writeLocal(key, lab.starter);
            setResults([]);
            setStatus("Starter restored");
          }}
        >
          Restore starter
        </button>
      </div>
      <p role="status">{status}</p>
      {code !== executed.current && results.length > 0 && (
        <p>
          These results belong to the previous code. Run the current version to
          update them.
        </p>
      )}
      <ul className="lab-results">
        {results.map((row) => (
          <li key={row.name} className={row.passed ? "passed" : "failed"}>
            <strong>
              {row.passed ? "PASS" : "REVISE"} · {row.name}
            </strong>
            <pre>{row.detail}</pre>
          </li>
        ))}
      </ul>
      {output && (
        <details open>
          <summary>Program output</summary>
          <pre>{output}</pre>
        </details>
      )}
      <details className="practice-reference">
        <summary>Compare the complete reference implementation</summary>
        <TeachingMarkdown>
          {"```python\n" + lab.solution + "\n```"}
        </TeachingMarkdown>
      </details>
      <small>
        Python runs in a separate browser sandbox. No academy server execution,
        credentials, third-party packages or model calls. Results are
        browser-reported self-study evidence, not an independently verified
        grade. Runtime files are served by this app.
      </small>
      {run > 0 && (
        <iframe
          key={run}
          ref={frame}
          src="/sandbox/index.html"
          sandbox="allow-scripts"
          title="Isolated Python execution"
          className="runner-frame"
        />
      )}
    </section>
  );
}
