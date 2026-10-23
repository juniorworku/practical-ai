import { useEffect, useState } from "react";
import { TeachingMarkdown } from "./ConceptReader";
import LiveSessions from "./LiveSessions";
import { api } from "./api";
import type { Profile, Program, ReviewQueue, Submission } from "./types";
type Plan = {
  goal: string;
  hours_per_week: number;
  diagnostic: Record<string, string>;
};
const diagnostic = [
  {
    id: "python",
    question: 'What does len(["a", "b"]) return?',
    options: ["2", "The last item", "An error"],
    correct: "a",
    explanation:
      "len returns the number of items. Practise functions, lists, dictionaries and assertions before the Agent or Engineering path.",
  },
  {
    id: "http",
    question: "An API returns HTTP 429. What is the appropriate response?",
    options: [
      "Retry immediately forever",
      "Use bounded retries and respect Retry-After",
      "Put the credential in the browser",
    ],
    correct: "b",
    explanation:
      "429 indicates a rate limit. Respect Retry-After and an overall deadline; never retry indefinitely.",
  },
  {
    id: "evaluation",
    question: "A model change improves a demo. How should you compare it?",
    options: [
      "Pick the nicest output",
      "Change the evaluation questions until it passes",
      "Run the same labeled cases and compare failures, latency and cost",
    ],
    correct: "c",
    explanation:
      "Keep cases fixed so the comparison is meaningful. Report failures and cost, not just fluent output.",
  },
];
const goals = [
  ["workflow", "Build useful workflows"],
  ["agents", "Build tool-using agents"],
  ["engineering", "Engineer and deploy AI systems"],
  ["freelancing", "Deliver AI services for clients"],
  ["foundations", "Build foundations and explore"],
] as const;
export default function LearningHub({
  profile,
  programs,
  onOpen,
  onLesson,
}: {
  profile: Profile;
  programs: Program[];
  onOpen: (program: Program) => void;
  onLesson: (program: Program, id: number) => void;
}) {
  const [plan, setPlan] = useState<Plan>({
    goal: "workflow",
    hours_per_week: 4,
    diagnostic: {},
  });
  const [saved, setSaved] = useState<Plan | null>(null);
  const [queue, setQueue] = useState<ReviewQueue | null>(null);
  const [status, setStatus] = useState("");
  const [revealed, setRevealed] = useState(false);
  useEffect(() => {
    let alive = true;
    Promise.allSettled([
      api<Plan|undefined>("learning-plan/"),api<ReviewQueue>("review-queue/")
    ]).then(([planResult,reviewResult])=>{
      if(!alive)return
      if(planResult.status==='fulfilled'&&planResult.value){setPlan(planResult.value);setSaved(planResult.value)}
      if(reviewResult.status==='fulfilled')setQueue(reviewResult.value)
      const errors=[planResult,reviewResult].filter(result=>result.status==='rejected').map(result=>String((result as PromiseRejectedResult).reason))
      if(errors.length)setStatus(errors.join(' · '))
    })
    return () => {
      alive = false;
    };
  }, []);
  const selected = programs.find(
    (p) =>
      p.slug ===
      {
        workflow: "ai-workshops",
        agents: "ai-agent-bootcamp",
        engineering: "ai-engineering-12-week",
        freelancing: "freelancing-masterclass",
        foundations: "genai-accelerator",
      }[saved?.goal || "workflow"],
  );
  const card = queue?.due_cards[0];
  const needsPython = saved && saved.diagnostic.python !== "a";
  return (
    <section className="learning-hub">
      <details className="panel" open={!saved}>
        <summary>Find your starting point and make a weekly plan</summary>
        <form
          onSubmit={async (event) => {
            event.preventDefault();
            try {
              const data = await api<Plan>("learning-plan/", {
                method: "PUT",
                body: JSON.stringify(plan),
              });
              setSaved(data);
              setStatus(
                "Learning plan saved. Recommendations are guidance, not enrollment requirements.",
              );
            } catch (error) {
              setStatus((error as Error).message);
            }
          }}
        >
          <label>
            Your goal
            <select
              aria-label="Your goal"
              value={plan.goal}
              onChange={(event) =>
                setPlan({ ...plan, goal: event.target.value })
              }
            >
              {goals.map(([value, label]) => (
                <option value={value} key={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Hours you can practise each week
            <input
              aria-label="Hours you can practise each week"
                type="number"
              min={1}
              max={40}
              required
              value={plan.hours_per_week}
              onChange={(event) =>
                setPlan({ ...plan, hours_per_week: Number(event.target.value) })
              }
            />
          </label>
          <p>
            Three quick checks identify topics to revisit. These do not certify
            readiness or block a program.
          </p>
          {diagnostic.map((item) => (
            <fieldset key={item.id}>
              <legend>{item.question}</legend>
              {item.options.map((option, index) => (
                <label className="diagnostic-option" key={option}>
                  <input
                    type="radio"
                    required
                    name={item.id}
                    value={String.fromCharCode(97 + index)}
                    checked={
                      plan.diagnostic[item.id] ===
                      String.fromCharCode(97 + index)
                    }
                    onChange={(event) =>
                      setPlan({
                        ...plan,
                        diagnostic: {
                          ...plan.diagnostic,
                          [item.id]: event.target.value,
                        },
                      })
                    }
                  />
                  {option}
                </label>
              ))}
              {saved && (
                <p className="hint-box">
                  {saved.diagnostic[item.id] === item.correct
                    ? "Correct. "
                    : "Revisit this topic. "}
                  {item.explanation}
                </p>
              )}
            </fieldset>
          ))}
          <button className="button">Save my learning plan</button>
        </form>
      </details>
      {saved && selected && (
        <article className="panel">
          <span className="eyebrow">SUGGESTED INDEPENDENT PATH</span>
          <h3>{selected.title}</h3>
          <p>{selected.progression?.entry || selected.level}</p>
          <p>
            At {saved.hours_per_week} hours/week, allow approximately{" "}
            {Math.ceil(
              selected.lessons.reduce((sum, l) => sum + l.minutes, 0) /
                60 /
                saved.hours_per_week,
            )}{" "}
            weeks for the listed practice time. Projects and revision may take
            longer.
          </p>
          {needsPython && (
            <p>
              Start with Python functions, lists, dictionaries and assertions.
              Terminal Tutor helps with workspace commands; it is not a
              substitute for Python practice. Revisit the program’s setup
              lessons before attempting its projects.
            </p>
          )}
          {needsPython && (
            <details>
              <summary>Python bridge: trace a complete function</summary>
              <TeachingMarkdown>{`Start with one function, a list of dictionaries and an assertion. Run this in a fresh Python file before changing it.

1. A dictionary maps a key to a value: row["expected"] reads one field.
2. A list keeps rows in order. A for loop visits each row once.
3. A function accepts an input and returns a value. Indentation defines its body.
4. The counter starts at zero and increases only when the labels match.
5. An assertion fails loudly when observed behavior differs from the expected value.

\`\`\`python
def count_matches(rows):
    correct = 0
    for row in rows:
        if row["actual"] == row["expected"]:
            correct += 1
    return correct

cases = [
    {"expected": "answer", "actual": "answer"},
    {"expected": "abstain", "actual": "answer"},
 ]
assert count_matches(cases) == 1
assert count_matches([]) == 0
print("Both checks passed")
\`\`\`

Predict the result, then change the second actual label to abstain: the count becomes two and the first assertion must be updated only after you explain why. Deliberately return inside the loop to see why the empty-input case fails. Restore the correct indentation. These checks measure label agreement, not factual support.`}</TeachingMarkdown>
            </details>
          )}
          <p>
            Programs do not require completing GenAI Accelerator or another
            academy program.
          </p>
          <button className="text-button" onClick={() => onOpen(selected)}>
            Open suggested program
          </button>
        </article>
      )}
      <section className="panel">
        <h2>Practise today</h2>
        <p>
          Review comes from lessons you have opened. Recall schedules measure
          confidence; quiz and browser checks are shown separately.
        </p>
        {card ? (
          <>
            <span className="eyebrow">
              {queue?.due_cards.length} cards due in this batch
            </span>
            <h3>{card.front}</h3>
            {revealed && <p>{card.back}</p>}
            <button
              className="text-button"
              onClick={() => setRevealed(!revealed)}
            >
              {revealed ? "Hide answer" : "Reveal answer"}
            </button>
            {(["again", "hard", "good"] as const).map((rating) => (
              <button
                className="text-button"
                disabled={!revealed}
                key={rating}
                onClick={async () => {
                  try {
                    await api(`lessons/${card.lesson}/review-card/`, {
                      method: "POST",
                      body: JSON.stringify({ card: card.id, rating }),
                    });
                    setQueue(await api<ReviewQueue>("review-queue/"));
                    setRevealed(false);
                  } catch (error) {
                    setStatus((error as Error).message);
                  }
                }}
              >
                {rating}
              </button>
            ))}
          </>
        ) : (
          <p>
            No cards due yet. Open a lesson and practise its flashcards to build
            your review queue.
          </p>
        )}
        {queue?.missed_questions.length ? (
          <>
            <h3>Revisit recent quiz mistakes</h3>
            {queue.missed_questions.map((item, index) => (
              <button
                className="review-link"
                key={index}
                onClick={() => {
                  const program = programs.find((p) => p.slug === item.program);
                  if (program) onLesson(program, item.lesson);
                }}
              >
                <strong>{item.title}</strong>
                <span>{item.question}</span>
              </button>
            ))}
          </>
        ) : null}
      </section>
      <LiveSessions />
      <div className="progress-legend">
        <strong>Your evidence, kept separate</strong>
        <span>{profile.completed.length} read / self-marked complete</span>
        <span>{profile.progress.practised.length} with practice recorded</span>
        <span>
          {profile.progress.quiz_passed.length} with all quiz questions correct
        </span>
        <span>
          {profile.progress.lab_passed.length} with browser checks passed ·
          self-reported
        </span>
        <span>
          {profile.progress.reviewed.length} with a human-reviewed project
          revision
        </span>
      </div>
      <p role="status">{status}</p>
      {profile.is_staff && <ReviewerDesk />}
    </section>
  );
}
function ReviewerDesk() {
  const [rows, setRows] = useState<Submission[]>([]);
  const [feedback, setFeedback] = useState<Record<number, string>>({});
  const [status, setStatus] = useState("");
  useEffect(() => {
    api<Submission[]>("reviews/")
      .then(setRows)
      .catch((error) => setStatus((error as Error).message));
  }, []);
  return (
    <details className="panel">
      <summary>
        Staff project review queue · {rows.length} awaiting review
      </summary>
      <p>
        Inspect the exact artifact revision, reproduce the documented checks,
        and distinguish structural tests from factual support. Assess
        latency/cost/quality, context policy, failures and operational claims.
        Do not mark a review from a screenshot alone.
      </p>
      {rows.map((row) => (
        <article className="submission-row" key={row.id}>
          <h3>
            {row.student} · {row.lesson} · #{row.id}
          </h3>
          <p>
            <a href={row.artifact_url} target="_blank" rel="noreferrer">
              Submitted artifact
            </a>{" "}
            · {row.commit}
          </p>
          <pre>{row.evidence}</pre>
          <dl>
            {Object.entries(row.measurements).map(([key, value]) => (
              <div key={key}>
                <dt>{key}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
          <label>
            Specific findings, reproduction and next steps
            <textarea
              minLength={40}
              maxLength={12000}
              value={feedback[row.id] || ""}
              onChange={(event) =>
                setFeedback({ ...feedback, [row.id]: event.target.value })
              }
            />
          </label>
          {["changes_requested", "reviewed"].map((outcome) => (
            <button
              className="text-button"
              disabled={(feedback[row.id] || "").trim().length < 40}
              key={outcome}
              onClick={async () => {
                try {
                  await api("reviews/", {
                    method: "POST",
                    body: JSON.stringify({
                      id: row.id,
                      status: outcome,
                      feedback: feedback[row.id],
                    }),
                  });
                  setRows(await api<Submission[]>("reviews/"));
                  setStatus("Review saved and visible to the learner.");
                } catch (error) {
                  setStatus((error as Error).message);
                }
              }}
            >
              {outcome === "reviewed"
                ? "Record completed review"
                : "Request changes"}
            </button>
          ))}
        </article>
      ))}
      <p role="status">{status}</p>
    </details>
  );
}
