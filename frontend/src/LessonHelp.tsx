import { useEffect, useState } from "react";
import { api } from "./api";
import { storageKey, readLocal, writeLocal, removeLocal } from "./storage";
import type { Learning } from "./types";
type Question = {
  id: number;
  author: string;
  question: string;
  answer: string;
  answered_by: string | null;
};
export default function LessonHelp({
  lesson,
  learning,
}: {
  lesson: number;
  learning: Learning;
}) {
  const key = storageKey("question", lesson);
  const [question, setQuestion] = useState(() => readLocal<string>(key) || "");
  const [rows, setRows] = useState<Question[]>([]);
  const [topic, setTopic] = useState(0);
  const [hints, setHints] = useState(0);
  const [issue, setIssue] = useState(
    () => readLocal<string>(storageKey("issue", lesson)) || "",
  );
  const [staff, setStaff] = useState(false);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let alive = true;
    Promise.all([
      api<Question[]>(`lessons/${lesson}/questions/`),
      api<{ is_staff: boolean }>("me/"),
    ])
      .then(([data, me]) => {
        if (alive) {
          setRows(data);
          setStaff(me.is_staff);
        }
      })
      .catch((error) => {
        if (alive) setStatus(error.message);
      });
    return () => {
      alive = false;
    };
  }, [lesson]);
  const concept = learning.concepts[topic];
  const prompts = [
    "Predict the expected output for the smallest example. Which input changes that prediction?",
    concept
      ? `${concept.term}: ${concept.definition}`
      : "Identify the input, boundary and expected output.",
    ...(learning.exercise.hints || [learning.exercise.hint]),
  ];
  return (
    <section className="lesson-help">
      <h2>Get unstuck, one step at a time</h2>
      <p>
        This guide uses the current lesson’s authored concepts and hints. It
        does not inspect your code or use an AI model.
      </p>
      <label>
        Concept to revisit
        <select
          aria-label="Concept to revisit"
          value={topic}
          onChange={(event) => {
            setTopic(Number(event.target.value));
            setHints(0);
          }}
        >
          {learning.concepts.map((item, index) => (
            <option key={item.term} value={index}>
              {item.term}
            </option>
          ))}
        </select>
      </label>
      <ol>
        {prompts.slice(0, hints).map((prompt, index) => (
          <li key={index}>{prompt}</li>
        ))}
      </ol>
      <button
        className="text-button"
        disabled={hints >= prompts.length}
        onClick={() => setHints((value) => value + 1)}
      >
        Show next guiding question
      </button>
      <h3>Ask about this lesson</h3>
      <p>
        Questions are visible to enrolled learners and staff. Use synthetic
        examples and remove secrets or personal data. Staff can reply; a
        response time is not promised.
      </p>
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          setBusy(true);
          try {
            setRows(
              await api<Question[]>(`lessons/${lesson}/questions/`, {
                method: "POST",
                body: JSON.stringify({ question }),
              }),
            );
            setQuestion("");
            removeLocal(key);
            setStatus("Question posted to this lesson.");
          } catch (error) {
            setStatus((error as Error).message);
          } finally {
            setBusy(false);
          }
        }}
      >
        <label>
          Expected result, actual result and what you tried
          <textarea
            required
            minLength={30}
            maxLength={4000}
            rows={5}
            value={question}
            onChange={(event) => {
              setQuestion(event.target.value);
              writeLocal(key, event.target.value);
            }}
            placeholder="Expected: …\nActual: …\nSmallest synthetic example: …\nWhat I tried: …"
          />
        </label>
        <button className="button" disabled={busy}>
          Post lesson question
        </button>
      </form>
      {rows.map((row) => (
        <article className="question-row" key={row.id}>
          <strong>{row.author}</strong>
          <p>{row.question}</p>
          {row.answer ? (
            <div className="quiz-feedback">
              <strong>{row.answered_by} · staff reply</strong>
              <p>{row.answer}</p>
            </div>
          ) : (
            <small>Awaiting a staff reply</small>
          )}
          {staff && (
            <form
              onSubmit={async (event) => {
                event.preventDefault();
                setBusy(true);
                try {
                  await api(`questions/${row.id}/answer/`, {
                    method: "POST",
                    body: JSON.stringify({ answer: answers[row.id] }),
                  });
                  setRows(
                    await api<Question[]>(`lessons/${lesson}/questions/`),
                  );
                  setStatus("Staff reply saved.");
                } catch (error) {
                  setStatus((error as Error).message);
                } finally {
                  setBusy(false);
                }
              }}
            >
              <label>
                Staff explanation
                <textarea
                  required
                  minLength={20}
                  maxLength={6000}
                  value={answers[row.id] || ""}
                  onChange={(event) =>
                    setAnswers({ ...answers, [row.id]: event.target.value })
                  }
                />
              </label>
              <button className="button" disabled={busy}>
                Save staff reply
              </button>
            </form>
          )}
        </article>
      ))}
      <details>
        <summary>Report unclear teaching or a broken example</summary>
        <form
          onSubmit={async (event) => {
            event.preventDefault();
            setBusy(true);
            try {
              await api(`lessons/${lesson}/issues/`, {
                method: "POST",
                body: JSON.stringify({ description: issue }),
              });
              setIssue("");
              removeLocal(storageKey("issue", lesson));
              setStatus("Issue recorded with this lesson’s content revision.");
            } catch (error) {
              setStatus((error as Error).message);
            } finally {
              setBusy(false);
            }
          }}
        >
          <label>
            Chapter, steps to reproduce and what needs clarification
            <textarea
              required
              minLength={20}
              maxLength={4000}
              value={issue}
              onChange={(event) => {
                setIssue(event.target.value);
                writeLocal(storageKey("issue", lesson), event.target.value);
              }}
            />
          </label>
          <button className="button" disabled={busy}>
            Report content issue
          </button>
        </form>
      </details>
      <p role="status">{status}</p>
    </section>
  );
}
