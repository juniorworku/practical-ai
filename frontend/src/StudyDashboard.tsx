import { useEffect, useState } from "react";
import {
  ArrowRight,
  Bookmark,
  BookOpen,
  CheckCheck,
  Code2,
  FolderCheck,
  Sparkles,
} from "lucide-react";
import { api } from "./api";
import type { Program, Profile } from "./types";
export type BookmarkEntry = {
  lesson: number;
  program: string;
  program_title: string;
  title: string;
};
export default function StudyDashboard({
  profile,
  programs,
  onLesson,
  onExplore,
}: {
  profile: Profile;
  programs: Program[];
  onLesson: (program: Program, id: number) => void;
  onExplore: () => void;
}) {
  const [bookmarks, setBookmarks] = useState<BookmarkEntry[]>([]);
  const [status, setStatus] = useState("");
  const [showAll, setShowAll] = useState(false);
  useEffect(() => {
    let alive = true;
    api<BookmarkEntry[]>("bookmarks/")
      .then((data) => {
        if (alive) setBookmarks(data);
      })
      .catch((error) => {
        if (alive) setStatus(error.message);
      });
    return () => {
      alive = false;
    };
  }, []);
  const enrolled = programs.filter(
    (program) =>
      profile.enrolled.includes(program.id) && program.category !== "Library",
  );
  const current = [...enrolled].sort((a, b) =>
    String(profile.positions[b.id]?.updated_at || "").localeCompare(
      String(profile.positions[a.id]?.updated_at || ""),
    ),
  )[0];
  const lesson =
    current &&
    (current.lessons.find(
      (item) =>
        item.id === profile.positions[current.id]?.lesson &&
        !profile.completed.includes(item.id),
    ) ||
      current.lessons.find((item) => !profile.completed.includes(item.id)) ||
      current.lessons[0]);
  return (
    <section className="study-dashboard">
      <div className="dashboard-welcome">
        <div>
          <span className="eyebrow">
            {new Intl.DateTimeFormat("en", {
              weekday: "long",
              month: "long",
              day: "numeric",
            }).format(new Date())}
          </span>
          <h1>
            Welcome back, <em>{profile.display_name || profile.username}.</em>
          </h1>
          <p>
            A clear next step. A little deliberate practice. Something useful
            built.
          </p>
        </div>
        <button className="button secondary" onClick={onExplore}>
          Explore programs
          <ArrowRight size={16} />
        </button>
      </div>
      <div className="dashboard-focus">
        <article className="continue-card">
          <div>
            <span className="eyebrow">
              <span className="live-dot" />{" "}
              {current ? "YOUR NEXT STEP" : "MAKE YOUR FIRST MOVE"}
            </span>
            <h2>{lesson?.title || "Choose what you want to build."}</h2>
            <p>
              {current
                ? current.title
                : "Independent paths for workflows, agents, engineering and client delivery. All free to join."}
            </p>
            {current && (
              <div className="continue-progress">
                <progress
                  aria-label="Reading progress"
                  value={
                    current.lessons.filter((item) =>
                      profile.completed.includes(item.id),
                    ).length
                  }
                  max={current.lessons.length}
                />
                <small>
                  {
                    current.lessons.filter((item) =>
                      profile.completed.includes(item.id),
                    ).length
                  }{" "}
                  of {current.lessons.length} lessons marked read
                </small>
              </div>
            )}
            <button
              className="button"
              onClick={() =>
                current && lesson ? onLesson(current, lesson.id) : onExplore()
              }
            >
              {current ? "Resume learning" : "Find your program"}
              <ArrowRight size={17} />
            </button>
          </div>
          <div className="continue-illustration" aria-hidden="true">
            <div>
              <BookOpen size={35} />
            </div>
            <span>
              <Code2 size={18} />
              build
            </span>
            <span>
              <CheckCheck size={18} />
              evaluate
            </span>
          </div>
        </article>
        <article className="evidence-card">
          <span className="eyebrow">PROGRESS WITH PROOF</span>
          <h3>More than pages read.</h3>
          <div>
            <CheckCheck size={18} />
            <strong>{profile.progress.quiz_passed.length}</strong>
            <span>lessons with all quiz answers correct</span>
          </div>
          <div>
            <Code2 size={18} />
            <strong>{profile.progress.lab_passed.length}</strong>
            <span>browser check sets passed · self-reported</span>
          </div>
          <div>
            <FolderCheck size={18} />
            <strong>{profile.progress.reviewed.length}</strong>
            <span>lessons with reviewed project revisions</span>
          </div>
          <small>
            These measures describe different evidence. They are not a
            certification.
          </small>
        </article>
      </div>
      <section className="saved-lessons">
        <div className="compact-heading">
          <h2>
            <Bookmark size={19} />
            Saved for later
          </h2>
          <span>
            {bookmarks.length} {bookmarks.length === 1 ? "lesson" : "lessons"}
          </span>
        </div>
        {bookmarks.length ? (
          <div className="bookmark-grid">
            {bookmarks.slice(0, showAll ? undefined : 6).map((item) => (
              <button
                key={item.lesson}
                onClick={() => {
                  const program = programs.find((p) => p.slug === item.program);
                  if (program) onLesson(program, item.lesson);
                }}
              >
                <BookOpen size={18} />
                <div>
                  <small>{item.program_title}</small>
                  <strong>{item.title}</strong>
                </div>
                <ArrowRight size={15} />
              </button>
            ))}
          </div>
        ) : (
          <p className="bookmark-empty">
            <Sparkles size={16} />
            Save a lesson using its bookmark button. Your personal reading list
            will appear here.
          </p>
        )}
        {bookmarks.length > 6 && (
          <button className="text-button" onClick={() => setShowAll(!showAll)}>
            {showAll
              ? "Show fewer saved lessons"
              : `Show all ${bookmarks.length} saved lessons`}
          </button>
        )}
        {status && <p role="status">{status}</p>}
      </section>
    </section>
  );
}
