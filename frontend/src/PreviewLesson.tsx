import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import ConceptReader, { TeachingMarkdown } from "./ConceptReader";
import BrowserLab from "./BrowserLab";
import type { Lesson, Learning, Program } from "./types";
export default function PreviewLesson({
  program,
  onStart,
  onBack,
}: {
  program: Program;
  onStart: () => void;
  onBack: () => void;
}) {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [error, setError] = useState("");
  const [exercise, setExercise] = useState(false);
  const exercisePanel = useRef<HTMLElement>(null);
  useEffect(() => {
    if (!exercise) return;
    exercisePanel.current?.focus({ preventScroll: true });
    exercisePanel.current?.scrollIntoView({
      block: "start",
      behavior: "instant",
    });
  }, [exercise]);
  useEffect(() => {
    let alive = true;
    api<Lesson>(`programs/${program.slug}/preview/`, {}, false)
      .then((data) => {
        if (alive) setLesson(data);
      })
      .catch((error) => {
        if (alive) setError(error.message);
      });
    return () => {
      alive = false;
    };
  }, [program.slug]);
  const learning = lesson?.resources?.learning as Learning | undefined;
  return (
    <main className="wrap preview-lesson" id="main-content" tabIndex={-1}>
      <button className="text-button" onClick={onBack}>
        Back to syllabus
      </button>
      <span className="eyebrow">FREE PUBLIC LESSON PREVIEW</span>
      <h1>{lesson?.title || program.title}</h1>
      <p>
        Read a full lesson before joining. Create a free account to save your
        work and access its remaining activities.
      </p>
      {error && <p role="alert">{error}</p>}
      {learning ? (
        <ConceptReader
          preview
          learning={learning}
          onPractice={() => setExercise(true)}
        />
      ) : lesson ? (
        <TeachingMarkdown>{lesson.content}</TeachingMarkdown>
      ) : (
        <p role="status">Loading sample lesson…</p>
      )}
      {exercise && learning && (
        <section
          ref={exercisePanel}
          tabIndex={-1}
          aria-label="Preview exercise"
        >
          <h2>Try the exercise</h2>
          <ol>
            {learning.exercise.steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
          {learning.exercise.material && (
            <TeachingMarkdown>{learning.exercise.material}</TeachingMarkdown>
          )}
        </section>
      )}
      {lesson?.lab && (
        <BrowserLab lesson={lesson.id} lab={lesson.lab} preview />
      )}
      <button className="button" onClick={onStart}>
        Join for free and save progress
      </button>
    </main>
  );
}
