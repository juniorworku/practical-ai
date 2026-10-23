import { useEffect, useRef, useState } from "react";
import {
  BookOpen,
  BrainCircuit,
  Check,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  Code2,
  HelpCircle,
  Layers3,
  LoaderCircle,
  RotateCcw,
  Save,
} from "lucide-react";
import ConceptReader, { TeachingMarkdown } from "./ConceptReader";
import { api } from "./api";
import { readLocal, writeLocal, removeLocal, storageKey } from "./storage";
import useNotes from "./useNotes";
import BrowserLab from "./BrowserLab";
import ProjectEvidence from "./ProjectEvidence";
import LessonHelp from "./LessonHelp";
import type { Learning, Lesson, Practice, QuizResult } from "./types";
type Tab =
  | "lesson"
  | "exercise"
  | "questions"
  | "quiz"
  | "cards"
  | "task"
  | "notes"
  | "lab"
  | "help";
const tabs = [
  ["lesson", "Lesson", BookOpen],
  ["exercise", "Exercise", Code2],
  ["questions", "Questions", HelpCircle],
  ["quiz", "Quiz", BrainCircuit],
  ["cards", "Flashcards", Layers3],
  ["task", "Practical task", ClipboardCheck],
  ["notes", "Notes", Save],
  ["lab", "Python lab", Code2],
  ["help", "Get help", HelpCircle],
] as const;
export default function LearningStudio({
  lesson,
  learning,
  content,
  onError,
}: {
  lesson: Lesson;
  learning: Learning;
  content: string;
  onError: (message: string) => void;
}) {
  const [tab, setTab] = useState<Tab>(() => {
    const saved = readLocal<Tab>(storageKey("activity", lesson.id));
    return tabs.some(([id]) => id === saved && (id !== "lab" || lesson.lab))
      ? saved!
      : "lesson";
  });
  const panel = useRef<HTMLElement>(null);
  const focusActivity = useRef(false);
  function openActivity(next: Tab) {
    focusActivity.current = true;
    setTab(next);
  }
  useEffect(() => {
    if (!focusActivity.current) return;
    focusActivity.current = false;
    panel.current?.focus({ preventScroll: true });
    panel.current?.scrollIntoView({ block: "start", behavior: "instant" });
  }, [tab]);
  useEffect(() => {
    writeLocal(storageKey("activity", lesson.id), tab);
  }, [tab, lesson.id]);
  const [practice, setPractice] = useState<Practice | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState("");
  const [loadError, setLoadError] = useState("");
  const [quizAnswers, setQuizAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [card, setCard] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [hint, setHint] = useState(false);
  const [hintLevel, setHintLevel] = useState(0);
  const notebook = useNotes(lesson.id, lesson.notes || "");
  const draftKey = storageKey("practice", lesson.id);
  const [dirty, setDirty] = useState(false);
  const [blocked, setBlocked] = useState(false);
  const edits = useRef(0);
  const latest = useRef<Practice | null>(null);
  latest.current = practice;
  const availableTabs = tabs.filter((item) => item[0] !== "lab" || lesson.lab);
  useEffect(() => {
    let alive = true;
    api<Practice>(`lessons/${lesson.id}/practice/`)
      .then((data) => {
        if (alive) {
          const draft = readLocal<Practice>(draftKey);
          if (draft && draft.revision === data.revision) {
            setPractice({ ...data, ...draft });
            setDirty(true);
            if (draft.version !== data.version) {
              setBlocked(true);
              setSaved(
                "Saved practice changed elsewhere. Your local draft is retained; copy it before reloading.",
              );
            }
          } else setPractice(data);
          const quizDraft = readLocal<Record<string, string>>(
            storageKey("quiz-" + learning.revision, lesson.id),
          );
          setResult(quizDraft !== null ? null : data.last_quiz);
          setQuizAnswers(quizDraft ?? data.last_quiz?.answers ?? {});
        }
      })
      .catch((e) => {
        if (alive) setLoadError(e.message);
      });
    return () => {
      alive = false;
    };
  }, [lesson.id]);
  async function save(
    patch: Partial<Practice> = {},
    message = "Practice saved",
  ) {
    const current = latest.current;
    if (!current || saving || blocked) return;
    const sequence = edits.current;
    setSaving(true);
    setSaved("");
    try {
      const data = await api<Practice>(`lessons/${lesson.id}/practice/`, {
        method: "PUT",
        body: JSON.stringify({ ...current, ...patch }),
      });
      if (edits.current === sequence) {
        setPractice(data);
        setDirty(false);
        removeLocal(draftKey);
        setSaved(message);
      } else {
        setPractice((previous) =>
          previous ? { ...previous, version: data.version } : data,
        );
        setSaved("Newer draft retained · syncing…");
      }
      window.dispatchEvent(new Event("academy-progress"));
    } catch (error) {
      setSaved((error as Error).message + " Draft retained in this browser.");
      setBlocked(true);
    } finally {
      setSaving(false);
    }
  }
  useEffect(() => {
    if (!dirty || saving || blocked || !practice) return;
    writeLocal(draftKey, practice);
    const timer = window.setTimeout(
      () => void save({}, "Practice autosaved"),
      1100,
    );
    return () => window.clearTimeout(timer);
  }, [practice, dirty, saving, blocked]);
  async function grade() {
    setSaving(true);
    setSaved("");
    try {
      const graded = await api<QuizResult>(`lessons/${lesson.id}/quiz/`, {
        method: "POST",
        body: JSON.stringify({
          revision: learning.revision,
          answers: quizAnswers,
        }),
      });
      setResult(graded);
      removeLocal(storageKey("quiz-" + learning.revision, lesson.id));
      window.dispatchEvent(new Event("academy-progress"));
      setPractice((p) =>
        p
          ? {
              ...p,
              last_quiz: graded,
              attempt_count: p.attempt_count + 1,
              best_score: Math.max(p.best_score, graded.score),
            }
          : p,
      );
    } catch (e) {
      onError((e as Error).message);
    } finally {
      setSaving(false);
    }
  }
  function edit(patch: Partial<Practice>) {
    if (!latest.current) return;
    edits.current += 1;
    const next = { ...latest.current, ...patch };
    latest.current = next;
    setPractice(next);
    setDirty(true);
    setSaved(
      writeLocal(draftKey, next)
        ? "Draft saved in this browser · syncing…"
        : "Browser storage unavailable. Keep this lesson open until account sync succeeds.",
    );
  }
  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => {
      if (dirty && !readLocal(draftKey)) {
        event.preventDefault();
        event.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty, draftKey]);
  const activeCard = learning.flashcards[card];
  const hints = learning.exercise.hints || [learning.exercise.hint];
  return (
    <div className="learning-studio">
      <div
        className="lesson-tabs"
        role="tablist"
        aria-label="Lesson activities"
      >
        {availableTabs.map(([id, label, Icon]) => (
          <button
            key={id}
            id={`tab-${id}`}
            role="tab"
            aria-label={label}
            tabIndex={tab === id ? 0 : -1}
            onKeyDown={(event) => {
              const index = availableTabs.findIndex((item) => item[0] === id);
              const next =
                event.key === "ArrowRight"
                  ? (index + 1) % availableTabs.length
                  : event.key === "ArrowLeft"
                    ? (index - 1 + availableTabs.length) % availableTabs.length
                    : event.key === "Home"
                      ? 0
                      : event.key === "End"
                        ? availableTabs.length - 1
                        : -1;
              if (next >= 0) {
                event.preventDefault();
                setTab(availableTabs[next][0]);
                document
                  .getElementById(`tab-${availableTabs[next][0]}`)
                  ?.focus();
              }
            }}
            aria-selected={tab === id}
            aria-controls={`panel-${id}`}
            onClick={() => setTab(id)}
          >
            <Icon size={15} />
            {label}
            {id === "quiz" && result && (
              <span>
                {result.score}/{result.total}
              </span>
            )}
          </button>
        ))}
      </div>
      <div className="study-status">
        <span>
          <Check size={13} /> {learning.concepts.length} concepts ·{" "}
          {learning.quiz.length} quiz questions · {learning.flashcards.length}{" "}
          flashcards
        </span>
        <span role="status">
          {tab === "notes" ? notebook.message : saving ? "Saving…" : saved}
        </span>
      </div>
      {blocked && (
        <div className="hint-box">
          <p>Your draft is protected from overwriting a newer saved version.</p>
          <button
            className="text-button"
            onClick={() => {
              const blob = new Blob(
                [
                  JSON.stringify(
                    readLocal(draftKey + ":recovery") || practice,
                    null,
                    2,
                  ),
                ],
                {
                  type: "application/json",
                },
              );
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "recovered-practice.json";
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            Export recovery draft
          </button>
          <button
            className="text-button"
            onClick={() => {
              setBlocked(false);
              setSaved("Retrying account sync…");
            }}
          >
            Retry sync
          </button>
          <button
            className="text-button"
            onClick={async () => {
              try {
                const data = await api<Practice>(
                  `lessons/${lesson.id}/practice/`,
                );
                writeLocal(draftKey + ":recovery", practice);
                removeLocal(draftKey);
                setPractice(data);
                setDirty(false);
                setBlocked(false);
                setSaved(
                  "Account practice loaded; previous browser draft retained for export.",
                );
              } catch (error) {
                onError((error as Error).message);
              }
            }}
          >
            Load account practice and retain browser backup
          </button>
        </div>
      )}
      {!blocked && !!readLocal(draftKey + ":recovery") && (
        <button
          className="text-button"
          onClick={() => {
            const url = URL.createObjectURL(
              new Blob(
                [JSON.stringify(readLocal(draftKey + ":recovery"), null, 2)],
                { type: "application/json" },
              ),
            );
            const link = document.createElement("a");
            link.href = url;
            link.download = "practice-recovery.json";
            link.click();
            URL.revokeObjectURL(url);
          }}
        >
          Export earlier practice recovery draft
        </button>
      )}
      <section
        ref={panel}
        tabIndex={0}
        id={`panel-${tab}`}
        role="tabpanel"
        aria-labelledby={`tab-${tab}`}
        className="activity-panel"
      >
        {tab === "lesson" &&
          (learning.chapters?.length ? (
            <ConceptReader
              lessonId={lesson.id}
              learning={learning}
              onPractice={() => openActivity("exercise")}
            />
          ) : (
            <TeachingMarkdown>{content}</TeachingMarkdown>
          ))}
        {tab === "lab" && lesson.lab && (
          <BrowserLab lesson={lesson.id} lab={lesson.lab} />
        )}
        {tab === "help" && (
          <LessonHelp lesson={lesson.id} learning={learning} />
        )}
        {tab === "exercise" && (
          <>
            <div className="activity-heading">
              <span className="eyebrow">PRACTICE WITH GUIDANCE</span>
              <h2>Make the concept work.</h2>
              <p>
                Work through these steps in your own program workspace. Predict
                the result first, then record what you actually observe.
              </p>
            </div>
            <ol className="exercise-steps">
              {learning.exercise.steps.map((step, index) => (
                <li key={step}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <p>{step}</p>
                </li>
              ))}
            </ol>
            <button
              className="text-button"
              onClick={() => {
                setHint(!hint);
                setHintLevel(Math.max(1, hintLevel));
              }}
            >
              <HelpCircle size={16} />
              {hint ? "Hide the hint" : "I’d like a hint"}
            </button>
            {hint && (
              <div className="hint-box">
                <ol>
                  {hints.slice(0, hintLevel).map((text, index) => (
                    <li key={text}>
                      <strong>Hint {index + 1}: </strong>
                      {text}
                    </li>
                  ))}
                </ol>
                {hintLevel < hints.length && (
                  <button
                    className="text-button"
                    onClick={() => setHintLevel((level) => level + 1)}
                  >
                    Show next hint
                  </button>
                )}
              </div>
            )}
            {learning.exercise.material && (
              <div className="inline-practice">
                <TeachingMarkdown>
                  {learning.exercise.material}
                </TeachingMarkdown>
              </div>
            )}
            {learning.exercise.solution && (
              <details className="practice-reference">
                <summary>Compare with the complete reference solution</summary>
                <p>
                  Make your own attempt first. Compare the assertions and
                  explain differences; reading this solution does not run or
                  grade your code.
                </p>
                <TeachingMarkdown>
                  {learning.exercise.solution}
                </TeachingMarkdown>
              </details>
            )}
            <button
              className="button"
              onClick={() => openActivity("questions")}
            >
              Reflect on your approach <ChevronRight size={16} />
            </button>
          </>
        )}
        {tab !== "lesson" &&
          tab !== "exercise" &&
          tab !== "lab" &&
          tab !== "help" &&
          (!practice ? (
            <div className="practice-loading" role="status">
              {loadError ? (
                <p>{loadError} Reopen the lesson to retry.</p>
              ) : (
                <>
                  <LoaderCircle className="spin" size={18} />
                  Loading saved practice…
                </>
              )}
            </div>
          ) : (
            <fieldset disabled={saving} className="activity-fields">
              {tab === "questions" && (
                <>
                  <div className="activity-heading">
                    <span className="eyebrow">
                      EXPLAIN IT IN YOUR OWN WORDS
                    </span>
                    <h2>Think through the trade-off.</h2>
                    <p>
                      Your response is private and saved to this lesson. Open
                      questions are reflection, not automatically graded
                      answers.
                    </p>
                  </div>
                  {learning.questions.map((q) => (
                    <div className="reflection-item" key={q.id}>
                      <label className="reflection-question">
                        {q.prompt}
                        <textarea
                          aria-label="Reflection response"
                          rows={7}
                          maxLength={6000}
                          value={practice.reflection_answers[q.id] || ""}
                          onChange={(e) =>
                            edit({
                              reflection_answers: {
                                ...practice.reflection_answers,
                                [q.id]: e.target.value,
                              },
                            })
                          }
                          placeholder="State your decision, the evidence you would collect, and what would change your mind."
                        />
                      </label>
                      {q.guidance && (
                        <details className="reflection-guidance">
                          <summary>Compare your reasoning</summary>
                          <p>{q.guidance}</p>
                        </details>
                      )}
                    </div>
                  ))}
                  <button
                    className="button"
                    onClick={() => save({}, "Reflection saved")}
                  >
                    <Save size={15} />
                    Save reflection
                  </button>
                </>
              )}
              {tab === "quiz" && (
                <>
                  <div className="activity-heading">
                    <span className="eyebrow">KNOWLEDGE CHECK</span>
                    <h2>Apply what you learned.</h2>
                    <p>
                      Choose an answer for each question. You’ll receive an
                      explanation after submitting, and you can retry.
                    </p>
                  </div>
                  <div className="quiz-summary">
                    <span>
                      Best: {practice.best_score}/{learning.quiz.length}
                    </span>
                    <span>{practice.attempt_count} saved attempts</span>
                  </div>
                  {learning.quiz.map((q, index) => {
                    const reviewChapter = q.review_chapter || 'concept-tutorial';
                    const feedback = result?.feedback.find(
                      (f) => f.id === q.id,
                    );
                    return (
                      <fieldset className="quiz-question" key={q.id}>
                        <legend>
                          {index + 1}. {q.prompt}
                        </legend>
                        {q.options.map((option) => (
                          <label
                            key={option.id}
                            className={`${quizAnswers[q.id] === option.id ? "chosen " : ""}${feedback?.correct_option === option.id ? "right-answer" : ""}`}
                          >
                            <input
                              type="radio"
                              name={`quiz-${lesson.id}-${q.id}`}
                              value={option.id}
                              checked={quizAnswers[q.id] === option.id}
                              onChange={() => {
                                setQuizAnswers((a) => {
                                  const next = { ...a, [q.id]: option.id };
                                  writeLocal(
                                    storageKey(
                                      "quiz-" + learning.revision,
                                      lesson.id,
                                    ),
                                    next,
                                  );
                                  return next;
                                });
                                setResult(null);
                              }}
                            />
                            <span>{option.text}</span>
                          </label>
                        ))}
                        {feedback && (
                          <div
                            className={
                              feedback.correct
                                ? "quiz-feedback correct"
                                : "quiz-feedback retry"
                            }
                          >
                            <strong>
                              {feedback.correct
                                ? "Correct."
                                : "Review this concept."}
                            </strong>
                            <p>{feedback.explanation}</p>
                            {learning.chapters?.some(
                              (c) => c.id === reviewChapter,
                            ) && (
                              <button
                                className="text-button"
                                aria-label={`Review explanation for question ${index + 1}`}
                                onClick={() => {
                                  writeLocal(
                                    storageKey("chapter", lesson.id),
                                    reviewChapter,
                                  );
                                  openActivity("lesson");
                                }}
                              >
                                Review the lesson explanation{" "}
                                <BookOpen size={14} />
                              </button>
                            )}
                          </div>
                        )}
                      </fieldset>
                    );
                  })}
                  {result ? (
                    <div className="quiz-result" role="status">
                      <strong>
                        {result.score} of {result.total} correct
                      </strong>
                      <p>
                        {result.score === result.total
                          ? "You applied the lesson concepts correctly. Try explaining why the other options fail."
                          : "Use the explanations to revisit the lesson, then try another attempt."}
                      </p>
                      <button
                        className="text-button"
                        onClick={() => {
                          setQuizAnswers({});
                          writeLocal(
                            storageKey("quiz-" + learning.revision, lesson.id),
                            {},
                          );
                          setResult(null);
                        }}
                      >
                        <RotateCcw size={15} />
                        Try again
                      </button>
                    </div>
                  ) : (
                    <button
                      className="button"
                      disabled={
                        saving ||
                        Object.keys(quizAnswers).length !== learning.quiz.length
                      }
                      onClick={grade}
                    >
                      Check my answers <Check size={16} />
                    </button>
                  )}
                </>
              )}
              {tab === "cards" && (
                <>
                  <div className="activity-heading">
                    <span className="eyebrow">ACTIVE RECALL</span>
                    <h2>A small review, a stronger memory.</h2>
                    <p>
                      Say the answer before revealing it. “I know this” records
                      your own confidence; it isn’t a test score.
                    </p>
                  </div>
                  <div className="flashcard-progress">
                    <span>
                      Card {card + 1} of {learning.flashcards.length}
                    </span>
                    <span>{practice.known_cards.length} marked known</span>
                  </div>
                  <button
                    className={`flashcard ${flipped ? "flipped" : ""}`}
                    onClick={() => setFlipped(!flipped)}
                    aria-label={
                      flipped
                        ? "Hide flashcard answer"
                        : "Reveal flashcard answer"
                    }
                  >
                    <span className="eyebrow">
                      {flipped ? "THE IDEA" : "WHAT DOES THIS MEAN?"}
                    </span>
                    <strong>
                      {flipped ? activeCard.back : activeCard.front}
                    </strong>
                    <small>
                      {flipped
                        ? "Click to return to the question"
                        : "Think first. Click to reveal."}
                    </small>
                  </button>
                  <div className="recall-ratings">
                    <p>Schedule your next recall attempt:</p>
                    {(["again", "hard", "good"] as const).map((rating) => (
                      <button
                        key={rating}
                        className="text-button"
                        disabled={!flipped}
                        onClick={async () => {
                          try {
                            const result = await api<{ due_at: string }>(
                              `lessons/${lesson.id}/review-card/`,
                              {
                                method: "POST",
                                body: JSON.stringify({
                                  card: activeCard.id,
                                  rating,
                                }),
                              },
                            );
                            setSaved(
                              "Next review: " +
                                new Date(result.due_at).toLocaleString(),
                            );
                            setCard((card + 1) % learning.flashcards.length);
                            setFlipped(false);
                          } catch (error) {
                            onError((error as Error).message);
                          }
                        }}
                      >
                        {rating === "again"
                          ? "Again · 10 min"
                          : rating === "hard"
                            ? "Hard · tomorrow"
                            : "Good · 3+ days"}
                      </button>
                    ))}
                  </div>
                  <div className="flashcard-controls">
                    <button
                      className="icon-button"
                      aria-label="Previous flashcard"
                      onClick={() => {
                        setCard(
                          (card - 1 + learning.flashcards.length) %
                            learning.flashcards.length,
                        );
                        setFlipped(false);
                      }}
                    >
                      <ChevronLeft />
                    </button>
                    <button
                      className="button"
                      onClick={() => {
                        const known = practice.known_cards.includes(
                          activeCard.id,
                        )
                          ? practice.known_cards.filter(
                              (id) => id !== activeCard.id,
                            )
                          : [...practice.known_cards, activeCard.id];
                        void save(
                          { known_cards: known },
                          "Flashcard review saved",
                        );
                      }}
                    >
                      {practice.known_cards.includes(activeCard.id)
                        ? "Review this again"
                        : "I know this"}
                      <Check size={15} />
                    </button>
                    <button
                      className="icon-button"
                      aria-label="Next flashcard"
                      onClick={() => {
                        setCard((card + 1) % learning.flashcards.length);
                        setFlipped(false);
                      }}
                    >
                      <ChevronRight />
                    </button>
                  </div>
                </>
              )}
              {tab === "task" && (
                <>
                  <div className="activity-heading">
                    <span className="eyebrow">YOUR PRACTICAL DELIVERABLE</span>
                    <h2>Build it. Test it. Show your evidence.</h2>
                    <p>{learning.task.title}</p>
                  </div>
                  <div className="task-artifact">
                    <ClipboardCheck size={21} />
                    <div>
                      <small>SAVE THIS ARTIFACT IN YOUR WORKSPACE</small>
                      <code>{learning.task.deliverable}</code>
                    </div>
                    <span className="task-state">
                      {practice.task_status === "submitted"
                        ? "Submitted · self-reported"
                        : "Draft"}
                    </span>
                  </div>
                  <h3 className="checklist-title">Acceptance checklist</h3>
                  <p className="activity-note">
                    Only check a criterion after you have observed it. The
                    academy records your report and does not run or inspect your
                    local code.
                  </p>
                  <div className="acceptance-checklist">
                    {learning.task.criteria.map((criterion, index) => (
                      <label key={criterion}>
                        <input
                          type="checkbox"
                          checked={practice.checked_criteria.includes(index)}
                          onChange={(e) =>
                            edit({
                              checked_criteria: e.target.checked
                                ? [...practice.checked_criteria, index]
                                : practice.checked_criteria.filter(
                                    (i) => i !== index,
                                  ),
                              task_status: "draft",
                            })
                          }
                        />
                        <span>{criterion}</span>
                      </label>
                    ))}
                  </div>
                  <label className="evidence-label">
                    Your evidence & observations
                    <textarea
                      rows={7}
                      aria-label="Your evidence & observations"
                      maxLength={12000}
                      value={practice.task_evidence}
                      onChange={(e) =>
                        edit({
                          task_evidence: e.target.value,
                          task_status: "draft",
                        })
                      }
                      placeholder="Describe what you built, commands or checks you actually ran, observed outputs, failed cases, and remaining limitations. Use synthetic examples. Do not paste credentials."
                    />
                  </label>
                  <div className="task-actions">
                    <button
                      className="text-button"
                      onClick={() =>
                        save({ task_status: "draft" }, "Task draft saved")
                      }
                    >
                      <Save size={15} />
                      Save draft
                    </button>
                    <button
                      className="button"
                      onClick={() =>
                        save(
                          { task_status: "submitted" },
                          "Practical task submitted",
                        )
                      }
                    >
                      <ClipboardCheck size={16} />
                      Submit practical task
                    </button>
                  </div>
                  <small className="activity-note">
                    Submission needs at least 80 characters of evidence and
                    every acceptance criterion checked. It records completion of
                    your report, not an instructor grade.
                  </small>
                </>
              )}
              {tab === "task" && (
                <ProjectEvidence
                  lesson={lesson.id}
                  programSlug={lesson.program_slug}
                />
              )}
              {tab === "notes" && (
                <>
                  <div className="activity-heading">
                    <span className="eyebrow">YOUR LEARNING NOTEBOOK</span>
                    <h2>Keep the useful bits.</h2>
                    <p>
                      Notes autosave to your account. A recovery draft is also
                      kept in this browser until syncing succeeds.
                    </p>
                  </div>
                  {notebook.blocked && (
                    <div className="hint-box">
                      <button
                        className="text-button"
                        onClick={notebook.exportDraft}
                      >
                        Export notes recovery draft
                      </button>
                      <button
                        className="text-button"
                        onClick={() => void notebook.loadAccount()}
                      >
                        Load account notes and retain browser backup
                      </button>
                    </div>
                  )}
                  <label className="learner-notes">
                    Your notes & observations
                    <textarea
                      rows={10}
                      aria-label="Your notes & observations"
                      value={notebook.notes}
                      onChange={(e) => notebook.edit(e.target.value)}
                      maxLength={10000}
                    />
                  </label>
                  <button
                    className="button"
                    onClick={() => void notebook.save()}
                  >
                    <Save size={15} />
                    Save notes
                  </button>
                  <button
                    className="text-button"
                    onClick={notebook.exportDraft}
                  >
                    Export notes or recovery draft
                  </button>
                </>
              )}
            </fieldset>
          ))}
      </section>
    </div>
  );
}
