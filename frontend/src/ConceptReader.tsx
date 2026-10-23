import { useEffect, useRef, useState, type ReactNode } from "react";
import { api } from "./api";
import { storageKey, readLocal, writeLocal } from "./storage";
import { ArrowLeft, ArrowRight, BookOpen, Check } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Learning } from "./types";

function CopyBlock({ children }: { children: ReactNode }) {
  const pre = useRef<HTMLPreElement>(null);
  const [message, setMessage] = useState("Copy code");
  return (
    <div className="code-block">
      <button
        className="copy-code"
        onClick={async () => {
          try {
            await navigator.clipboard.writeText(pre.current?.innerText || "");
            setMessage("Copied");
          } catch {
            setMessage("Select code to copy");
          }
        }}
      >
        {message}
      </button>
      <pre ref={pre}>{children}</pre>
    </div>
  );
}
export function TeachingMarkdown({ children }: { children: string }) {
  return (
    <div className="markdown-reader">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        skipHtml
        components={{
          img: () => null,
          pre: ({ children }) => <CopyBlock>{children}</CopyBlock>,
          a: ({ children }) => <span>{children}</span>,
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}

export default function ConceptReader({
  learning,
  onPractice,
  initialChapterId,
  lessonId,
  preview = false,
}: {
  learning: Learning;
  onPractice: () => void;
  initialChapterId?: string;
  lessonId?: number;
  preview?: boolean;
}) {
  const chapters = learning.chapters || [];
  const key = storageKey("chapter", lessonId || "preview");
  const [chapter, setChapter] = useState(() =>
    Math.max(
      0,
      chapters.findIndex(
        (c) => c.id === (initialChapterId || readLocal<string>(key)),
      ),
    ),
  );
  const [syncError, setSyncError] = useState("");
  useEffect(()=>{
    const restore=()=>{
      const id=new URLSearchParams(location.hash.split('?')[1]).get('chapter')
      const index=chapters.findIndex(item=>item.id===id)
      if(index>=0)setChapter(index)
    }
    window.addEventListener('hashchange',restore)
    return()=>window.removeEventListener('hashchange',restore)
  },[lessonId])

  useEffect(() => {
    if (initialChapterId) {
      const index = chapters.findIndex((c) => c.id === initialChapterId);
      if (index >= 0) setChapter(index);
    }
  }, [initialChapterId]);
  useEffect(() => {
    if (!lessonId || preview || !chapters[chapter]) return;
    const id = chapters[chapter].id;
    writeLocal(key, id);
    if (location.hash.startsWith("#/learn/"))
      history.replaceState(
        null,
        "",
        location.hash.split("?")[0] + "?chapter=" + encodeURIComponent(id),
      );
    void api(`lessons/${lessonId}/position/`, {
      method: "PUT",
      body: JSON.stringify({ chapter: id }),
    }).catch(() =>
      setSyncError(
        "Reading position saved on this browser; account sync unavailable.",
      ),
    );
  }, [chapter, lessonId, preview, key]);
  useEffect(() => {
    if (!lessonId || preview) return;
    const scrollKey = storageKey(
      "reading-scroll",
      `${lessonId}:${chapters[chapter]?.id}`,
    );
    const saved = readLocal<number>(scrollKey);
    const restore = window.setTimeout(() => {
      if (saved !== null) window.scrollTo(0, saved);
    }, 100);
    let timer: number | undefined;
    const track = () => {
      window.clearTimeout(timer);
      timer = window.setTimeout(
        () => writeLocal(scrollKey, window.scrollY),
        150,
      );
    };
    window.addEventListener("scroll", track, { passive: true });
    return () => {
      window.clearTimeout(restore);
      window.clearTimeout(timer);
      window.removeEventListener("scroll", track);
    };
  }, [chapter, lessonId, preview]);
  const active = chapters[chapter];
  function select(index: number) {
    setChapter(index);
    document
      .getElementById("chapter-reading")
      ?.scrollIntoView({ block: "start", behavior: "smooth" });
  }
  if (!active) return null;
  return (
    <div className="course-book">
      {syncError && <p role="status">{syncError}</p>}
      <div className="book-intro">
        <span className="eyebrow">THE LESSON BOOK</span>
        <p>
          Read the concept chapters and implementation, then work through the
          case. The Exercise tab contains the input, walkthrough, checks and
          failure experiments.
        </p>
      </div>
      <details className="book-contents">
        <summary>
          <BookOpen size={16} />
          <span>Contents · {chapters.length} chapters</span>
          <strong>{active.title}</strong>
        </summary>
        <nav className="chapter-index" aria-label="Lesson chapters">
          {chapters.map((item, index) => (
            <button
              key={item.id}
              aria-current={chapter === index ? "step" : undefined}
              onClick={() => select(index)}
            >
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <small>{item.kind}</small>
                <strong>{item.title}</strong>
              </div>
              {chapter === index ? (
                <BookOpen size={15} />
              ) : (
                <ArrowRight size={15} />
              )}
            </button>
          ))}
        </nav>
      </details>
      <article
        id="chapter-reading"
        className="chapter-reading"
        aria-label="Chapter reading"
      >
        <div className="chapter-caption">
          <span className="eyebrow">
            CHAPTER {chapter + 1} OF {chapters.length} · {active.kind}
          </span>
          <span>
            ~{Math.max(1, Math.ceil(active.body.split(/\s+/).length / 180))} min
            reading
          </span>
        </div>
        <h2>{active.title}</h2>
        <TeachingMarkdown>{active.body}</TeachingMarkdown>
      </article>
      <div className="chapter-actions">
        <button
          className="text-button"
          disabled={chapter === 0}
          onClick={() => select(chapter - 1)}
        >
          <ArrowLeft size={16} />
          Previous chapter
        </button>
        {chapter < chapters.length - 1 ? (
          <button className="button" onClick={() => select(chapter + 1)}>
            Next chapter
            <ArrowRight size={16} />
          </button>
        ) : (
          <button className="button" onClick={onPractice}>
            Begin the exercise
            <ArrowRight size={16} />
          </button>
        )}
      </div>
      <details className="lesson-glossary">
        <summary>
          {learning.concepts.length} concepts explained in this lesson
        </summary>
        <dl>
          {learning.concepts.map((c) => (
            <div key={c.term}>
              <dt>
                <Check size={13} />
                {c.term}
              </dt>
              <dd>{c.definition}</dd>
            </div>
          ))}
        </dl>
      </details>
      {learning.attribution && (
        <details className="teaching-credit">
          <summary>Teaching credits & license</summary>
          <p>{learning.attribution.credit}</p>
          <small>
            Source snapshot {learning.attribution.revision.slice(0, 12)}. This
            lesson is taught here; no external course is required.
          </small>
          <pre>{learning.attribution.notice}</pre>
        </details>
      )}
    </div>
  );
}
