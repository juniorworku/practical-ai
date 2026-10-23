import { useEffect, useRef, useState, type ReactNode } from "react";
import { api } from "./api";
import { storageKey, readLocal, writeLocal } from "./storage";
import { ArrowLeft, ArrowRight, BookOpen } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { List } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
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
      <pre ref={pre} tabIndex={0} aria-label="Code example">
        {children}
      </pre>
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
  const [sections, setSections] = useState<{ id: string; title: string }[]>([]);
  const [activeSection, setActiveSection] = useState("");
  useEffect(() => {
    const headings = [
      ...(reading.current?.querySelectorAll<HTMLElement>(
        ".markdown-reader h2,.markdown-reader h3",
      ) || []),
    ];
    const items = headings.map((heading, index) => {
      heading.id = `reading-${lessonId || "preview"}-${chapter}-${index}`;
      heading.tabIndex = -1;
      return { id: heading.id, title: heading.textContent || "Section" };
    });
    setSections(items);
    setActiveSection(items[0]?.id || "");
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries)
          if (entry.isIntersecting) setActiveSection(entry.target.id);
      },
      { rootMargin: "-10% 0px -65% 0px", threshold: 0 },
    );
    headings.forEach((heading) => observer.observe(heading));
    return () => observer.disconnect();
  }, [chapter, lessonId]);
  function jumpToSection(id: string) {
    const target = document.getElementById(id);
    target?.focus({ preventScroll: true });
    target?.scrollIntoView({ block: "start", behavior: "instant" });
    setActiveSection(id);
  }
  const [syncError, setSyncError] = useState("");
  const selectedByStudent = useRef(false);
  const reading = useRef<HTMLElement>(null);
  const contents = useRef<HTMLDetailsElement>(null);
  useEffect(() => {
    const restore = () => {
      const id = new URLSearchParams(location.hash.split("?")[1]).get(
        "chapter",
      );
      const index = chapters.findIndex((item) => item.id === id);
      if (index >= 0) setChapter(index);
    };
    window.addEventListener("hashchange", restore);
    return () => window.removeEventListener("hashchange", restore);
  }, [lessonId]);

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
    const explicit = selectedByStudent.current;
    if (explicit) {
      selectedByStudent.current = false;
      if (contents.current) contents.current.open = false;
      const heading = reading.current?.querySelector<HTMLElement>("h2");
      heading?.focus({ preventScroll: true });
      reading.current?.scrollIntoView({ block: "start", behavior: "instant" });
    }
    if (!lessonId || preview) return;
    const scrollKey = storageKey(
      "reading-scroll",
      `${lessonId}:${chapters[chapter]?.id}`,
    );
    const saved = readLocal<number>(scrollKey);
    const restore = window.setTimeout(() => {
      if (!explicit && saved !== null) window.scrollTo(0, saved);
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
    if (index === chapter) {
      if (contents.current) contents.current.open = false;
      reading.current
        ?.querySelector<HTMLElement>("h2")
        ?.focus({ preventScroll: true });
      reading.current?.scrollIntoView({ block: "start", behavior: "instant" });
      return;
    }
    selectedByStudent.current = true;
    setChapter(index);
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
      <details ref={contents} className="book-contents">
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
      {sections.length > 0 && (
        <>
          <nav className="reading-outline" aria-label="On this page">
            <strong>
              <List size={15} />
              On this page
            </strong>
            {sections.map((section) => (
              <button
                key={section.id}
                aria-current={
                  activeSection === section.id ? "location" : undefined
                }
                onClick={() => jumpToSection(section.id)}
              >
                {section.title}
              </button>
            ))}
          </nav>
          <details className="mobile-reading-outline">
            <summary>On this page</summary>
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={(event) => {
                  jumpToSection(section.id);
                  event.currentTarget
                    .closest("details")
                    ?.removeAttribute("open");
                }}
              >
                {section.title}
              </button>
            ))}
          </details>
        </>
      )}
      <article
        ref={reading}
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
        <h2 tabIndex={-1}>{active.title}</h2>
        <TeachingMarkdown key={active.id}>{active.body}</TeachingMarkdown>
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
        <div className="concept-card-grid">
          {learning.concepts.map((concept) => (
            <Card key={concept.term}>
              <CardHeader>
                <CardTitle>{concept.term}</CardTitle>
              </CardHeader>
              <CardContent>
                <p>{concept.definition}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </details>
    </div>
  );
}
