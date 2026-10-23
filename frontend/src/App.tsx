import {
  useEffect,
  useRef,
  useState,
  lazy,
  Suspense,
  type FormEvent,
} from "react";
import {
  ArrowUpRight,
  ArrowRight,
  BookOpen,
  Bot,
  Check,
  ChevronDown,
  Clock3,
  Code2,
  GraduationCap,
  Layers3,
  LayoutDashboard,
  Menu,
  Play,
  Rocket,
  Sparkles,
  Terminal,
  X,
  BriefcaseBusiness,
  LogOut,
  CircleCheck,
  LoaderCircle,
  Search,
  UserRound,
  FolderCheck,
  Bookmark,
} from "lucide-react";
import InterfaceEffects from "./InterfaceEffects";
import CourseNavigation, { CourseModuleNav } from "./CourseNavigation";
import CourseOverview from "./CourseOverview";
import PasswordRecovery from "./PasswordRecovery";
import { readLocal, writeLocal, storageKey } from "./storage";
import { api, legacyHeaders } from "./api";
import AuthDialog from "./AuthDialog";
import type { SearchHit } from "./SearchDialog";
import StudyDashboard from "./StudyDashboard";
import type { Lesson, Program, Profile, Project } from "./types";

const LessonReader = lazy(() => import("./LessonReader"));
const LearningHub = lazy(() => import("./LearningHub"));
const PreviewLesson = lazy(() => import("./PreviewLesson"));
const SearchDialog = lazy(() => import("./SearchDialog"));
const AccountSettings = lazy(() => import("./AccountSettings"));
const StudentPortfolio = lazy(() => import("./StudentPortfolio"));

type Page =
  | "home"
  | "preview"
  | "course"
  | "dashboard"
  | "learn"
  | "accelerator"
  | "terminal"
  | "account"
  | "portfolio";
const icons = [Bot, Rocket, BriefcaseBusiness, Sparkles];
export default function App() {
  const [searchOpen, setSearchOpen] = useState(false);
  const [bookmarks, setBookmarks] = useState<number[]>([]);
  const [pendingRoute, setPendingRoute] = useState("");
  const [routeReady, setRouteReady] = useState(false);
  const [recovery, setRecovery] = useState<{
    uid?: string;
    token?: string;
  } | null>(null);
  const [page, setPage] = useState<Page>("home");
  const [programs, setPrograms] = useState<Program[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [selected, setSelected] = useState<Program | null>(null);
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [pendingProgram, setPendingProgram] = useState<Program | null>(null);
  const [auth, setAuth] = useState(false);
  const [register, setRegister] = useState(true);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [menu, setMenu] = useState(false);
  const [filter, setFilter] = useState("All programs");
  const [catalogQuery, setCatalogQuery] = useState("");
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [commandDraft, setCommandDraft] = useState("");
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [terminalLines, setTerminalLines] = useState([
    "Practical AI Terminal Tutor · simulated workspace",
    "Type help to see available commands. Your computer is never modified.",
  ]);
  const [command, setCommand] = useState("");
  const [terminalBusy, setTerminalBusy] = useState(false);
  const terminalOutput = useRef<HTMLPreElement>(null);
  useEffect(() => {
    const output = terminalOutput.current;
    if (output) output.scrollTop = output.scrollHeight;
  }, [terminalLines, terminalBusy]);
  const [lessonLoading, setLessonLoading] = useState(false);
  const [lessonSearch, setLessonSearch] = useState("");
  const [librarySearch, setLibrarySearch] = useState("");
  const [faq, setFaq] = useState<number | null>(0);
  async function refresh() {
    const me = await api<Profile>("me/");
    sessionStorage.setItem("academy-user", me.username);
    setProfile(me);
    return me;
  }
  async function loadPrograms() {
    setLoading(true);
    setError("");
    try {
      const data = await api<Program[]>("programs/", {}, false);
      setPrograms(data);
      return data;
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }
  function restoreRoute(catalog: Program[], me: Profile | null) {
    const [path, query] = location.hash.slice(1).split("?");
    const parts = (path || "/").split("/").filter(Boolean);
    if (parts[0] === "reset" && parts[1] && parts[2]) {
      setRecovery({ uid: parts[1], token: parts[2] });
      setPage("home");
      return;
    }
    const target = catalog.find((p) => p.slug === parts[1]);
    if (target && ["programs", "preview", "learn"].includes(parts[0])) {
      setSelected(target);
      if (parts[0] === "learn" && me?.enrolled.includes(target.id)) {
        const found =
          target.lessons.find((l) => l.id === Number(parts[2])) ||
          target.lessons[0];
        const chapter = new URLSearchParams(query).get("chapter");
        if (chapter) writeLocal(storageKey("chapter", found.id), chapter);
        setLesson((current) =>
          current?.id === found.id && current.resources ? current : found,
        );
        setPage("learn");
      } else {
        setPage(parts[0] === "preview" ? "preview" : "course");
        if (parts[0] === "learn" && !me) {
          setPendingRoute(location.hash);
          setAuth(true);
          setRegister(false);
        }
      }
    } else if (
      ["dashboard", "accelerator", "terminal", "account", "portfolio"].includes(
        parts[0],
      )
    ) {
      if (me) setPage(parts[0] as Page);
      else {
        setPendingRoute(location.hash);
        setPage("home");
        setAuth(true);
        setRegister(false);
      }
    } else setPage("home");
  }
  useEffect(() => {
    let alive = true;
    Promise.all([
      loadPrograms(),
      api<{ authenticated: boolean }>("auth/session/", {}, false).then(
        (state) =>
          state.authenticated || sessionStorage.getItem("academy-token")
            ? refresh().catch(() => null)
            : null,
      ),
    ]).then(([catalog, me]) => {
      if (alive) {
        restoreRoute(catalog || [], me);
        setRouteReady(true);
      }
    });
    const expired = () => {
      setProfile(null);
      setAuth(true);
      setRegister(false);
    };
    const progress = () => {
      void refresh().catch(() => {});
    };
    window.addEventListener("academy-expired", expired);
    window.addEventListener("academy-progress", progress);
    return () => {
      alive = false;
      window.removeEventListener("academy-expired", expired);
      window.removeEventListener("academy-progress", progress);
    };
  }, []);
  useEffect(() => {
    const back = () => restoreRoute(programs, profile);
    window.addEventListener("popstate", back);
    window.addEventListener("hashchange", back);
    return () => {
      window.removeEventListener("popstate", back);
      window.removeEventListener("hashchange", back);
    };
  }, [programs, profile]);
  useEffect(() => {
    if (!routeReady || recovery) return;
    const target =
      page === "home"
        ? "#/"
        : page === "course"
          ? `#/programs/${selected?.slug}`
          : page === "preview"
            ? `#/preview/${selected?.slug}`
            : page === "learn"
              ? `#/learn/${selected?.slug}/${lesson?.id}`
              : `#/${page}`;
    if (location.hash.split("?")[0] !== target)
      history.pushState(null, "", target);
    if (page === "learn" && selected && lesson) {
      writeLocal(storageKey("last-lesson", selected.id), lesson.id);
    }
  }, [routeReady, page, selected?.id, lesson?.id, recovery]);
  useEffect(() => {
    if (!lesson?.id || page !== "learn") return;
    let alive = true;
    setLessonLoading(true);
    api<Lesson>(`lessons/${lesson.id}/`)
      .then((full) => {
        if (alive) setLesson(full);
      })
      .catch((e) => {
        if (alive) setError(e.message);
      })
      .finally(() => {
        if (alive) setLessonLoading(false);
      });
    return () => {
      alive = false;
    };
  }, [lesson?.id, page]);
  useEffect(() => {
    if (page === "accelerator" && profile)
      api<Project[]>("projects/")
        .then(setProjects)
        .catch((e) => setError(e.message));
  }, [page, profile]);
  useEffect(() => {
    if (!profile) {
      setBookmarks([]);
      return;
    }
    api<{ lesson: number }[]>("bookmarks/")
      .then((items) => setBookmarks(items.map((item) => item.lesson)))
      .catch(() => {});
  }, [profile?.username]);
  useEffect(() => {
    const key = (event: KeyboardEvent) => {
      if (
        profile &&
        (event.metaKey || event.ctrlKey) &&
        event.key.toLowerCase() === "k"
      ) {
        event.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, [profile]);
  const pendingLessonFocus = useRef<number | null>(null);
  useEffect(() => {
    if (
      lessonLoading ||
      !lesson?.resources ||
      pendingLessonFocus.current !== lesson.id
    )
      return;
    pendingLessonFocus.current = null;
    const heading = document.querySelector<HTMLElement>(".lesson-content > h1");
    if (heading) {
      heading.tabIndex = -1;
      heading.focus({ preventScroll: true });
      heading.scrollIntoView({ block: "start", behavior: "instant" });
    }
  }, [lessonLoading, lesson]);
  function openLesson(program: Program, id: number) {
    pendingLessonFocus.current = id;
    setSelected(program);
    setLesson((current) =>
      current?.id === id && current.resources
        ? current
        : program.lessons.find((item) => item.id === id) || program.lessons[0],
    );
    setPage("learn");
    window.scrollTo(0, 0);
  }
  function openSearchHit(hit: SearchHit) {
    const program = programs.find((item) => item.slug === hit.program);
    if (program) openLesson(program, hit.lesson);
    setSearchOpen(false);
  }
  async function signOut() {
    try {
      await api("auth/session/logout/", { method: "POST" });
      sessionStorage.removeItem("academy-token");
      sessionStorage.removeItem("academy-user");
      setProfile(null);
      setSearchOpen(false);
      setPage("home");
    } catch (error) {
      setError((error as Error).message);
    }
  }
  async function toggleBookmark() {
    if (!lesson) return;
    setBusy(true);
    try {
      await api(`lessons/${lesson.id}/bookmark/`, {
        method: bookmarks.includes(lesson.id) ? "DELETE" : "POST",
      });
      setBookmarks((items) =>
        items.includes(lesson.id)
          ? items.filter((id) => id !== lesson.id)
          : [...items, lesson.id],
      );
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function navigate(next: Page) {
    if (
      next !== "home" &&
      !profile &&
      sessionStorage.getItem("academy-token")
    ) {
      try {
        await refresh();
        setPage(next);
        setMenu(false);
        setError("");
        window.scrollTo(0, 0);
        return;
      } catch {
        setAuth(true);
        return;
      }
    }
    if (next !== "home" && !profile) {
      setPendingRoute(`#/${next}`);
      setRegister(false);
      setError("Sign in to open your learning workspace.");
      setAuth(true);
      return;
    }
    setPage(next);
    setMenu(false);
    setError("");
    window.scrollTo(0, 0);
  }
  function goPrograms() {
    setPage("home");
    setMenu(false);
    setTimeout(
      () =>
        document
          .getElementById("programs")
          ?.scrollIntoView({ behavior: "smooth" }),
      0,
    );
  }
  function resumeLesson(program: Program, me: Profile) {
    const last =
      readLocal<number>(storageKey("last-lesson", program.id)) ||
      me.positions[program.id]?.lesson;
    const target =
      program.lessons.find((l) => l.id === last) ||
      program.lessons.find((l) => !me.completed.includes(l.id)) ||
      program.lessons[0];
    const position = me.positions[program.id];
    if (
      position?.lesson === target.id &&
      position.chapter &&
      !readLocal(storageKey("chapter", target.id))
    )
      writeLocal(storageKey("chapter", target.id), position.chapter);
    return target;
  }
  async function openProgram(program: Program) {
    if (!profile) {
      setSelected(program);
      setPendingProgram(program);
      setAuth(true);
      return;
    }
    setBusy(true);
    setError("");
    try {
      if (!profile.enrolled.includes(program.id))
        await api(`programs/${program.slug}/enroll/`, { method: "POST" });
      const me = await refresh();
      setLessonSearch("");
      setSelected(program);
      setLesson(resumeLesson(program, me));
      setPage("learn");
      window.scrollTo(0, 0);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function submitAuth(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const data = Object.fromEntries(new FormData(e.currentTarget));
    try {
      await api("auth/session/", {}, false);
      await api(
        `auth/session/${register ? "register" : "login"}/`,
        {
          method: "POST",
          body: JSON.stringify({ ...data, remember: data.remember === "on" }),
        },
        false,
      );
      sessionStorage.removeItem("academy-token");
      const signedIn = await refresh();
      setAuth(false);
      if (pendingProgram) {
        await api(`programs/${pendingProgram.slug}/enroll/`, {
          method: "POST",
        });
        const me = await refresh();
        setSelected(pendingProgram);
        setLesson(resumeLesson(pendingProgram, me));
        setPendingProgram(null);
        setPage("learn");
      } else if (pendingRoute) {
        const destination = pendingRoute;
        setPendingRoute("");
        history.replaceState(null, "", destination);
        restoreRoute(programs, signedIn);
      } else setPage("dashboard");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function toggleComplete() {
    if (!lesson || !profile) return;
    setBusy(true);
    setError("");
    try {
      await api(`lessons/${lesson.id}/complete/`, {
        method: profile.completed.includes(lesson.id) ? "DELETE" : "POST",
      });
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function createProject(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const form = e.currentTarget;
    try {
      const project = await api<Project>("projects/", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(new FormData(form))),
      });
      setActiveProject(project);
      setProjects((p) => [project, ...p]);
      form.reset();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function runCommand(e: FormEvent) {
    e.preventDefault();
    if (!command.trim() || terminalBusy) return;
    const entered = command.trim();
    setCommandHistory((history) =>
      [entered, ...history.filter((item) => item !== entered)].slice(0, 50),
    );
    setHistoryIndex(-1);
    setCommandDraft("");
    setCommand("");
    setTerminalBusy(true);
    try {
      const result = await api<{ output: string; hint: string }>("terminal/", {
        method: "POST",
        body: JSON.stringify({ command: entered }),
      });
      setTerminalLines((lines) => [
        ...lines,
        `$ ${entered}`,
        result.output,
        `↳ ${result.hint}`,
      ]);
    } catch (e) {
      setTerminalLines((lines) => [
        ...lines,
        `$ ${entered}`,
        (e as Error).message,
      ]);
    } finally {
      setTerminalBusy(false);
    }
  }
  function viewProgram(program: Program) {
    setSelected(program);
    setPage("course");
    setError("");
    window.scrollTo(0, 0);
  }
  const catalogPrograms = programs.filter((p) =>
    [
      "Cohort",
      "Workshop",
      "Masterclass",
      "Accelerator",
      "Engineering",
      "Tutor",
      "Advanced",
    ].includes(p.category),
  );
  const visiblePrograms = catalogPrograms.filter(
    (program) =>
      (filter === "All programs" || program.category === filter) &&
      [
        program.title,
        program.description,
        program.outcome,
        ...program.lessons.map((item) => item.title + " " + item.module),
      ]
        .join(" ")
        .toLowerCase()
        .includes(catalogQuery.trim().toLowerCase()),
  );
  const pageTitles: Partial<Record<Page, string>> = {
    home: "Learn it. Build it. Use it.",
    dashboard: "My learning",
    account: "Account & security",
    portfolio: "Project portfolio",
    accelerator: "GenAI Accelerator",
    terminal: "Terminal Tutor",
  };
  const pageTitle =
    page === "learn"
      ? lesson?.title || "Learning workspace"
      : page === "course"
        ? selected?.title || "Program"
        : page === "preview"
          ? `${selected?.title || "Program"} preview`
          : pageTitles[page] || "Academy";
  useEffect(() => {
    if (!menu) return;
    document.querySelector<HTMLElement>("#main-navigation button")?.focus();
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setMenu(false);
        document.querySelector<HTMLElement>(".mobile-toggle")?.focus();
      }
    };
    const outside = (event: PointerEvent) => {
      if (!(event.target as Element).closest(".header")) setMenu(false);
    };
    window.addEventListener("keydown", escape);
    window.addEventListener("pointerdown", outside);
    return () => {
      window.removeEventListener("keydown", escape);
      window.removeEventListener("pointerdown", outside);
    };
  }, [menu]);
  const acceleratorProgram = programs.find(
    (p) => p.slug === "genai-accelerator",
  );
  const terminalProgram = programs.find((p) => p.slug === "terminal-tutor");
  async function downloadProgram(program: Program) {
    setBusy(true);
    try {
      const response = await fetch(`/api/programs/${program.slug}/download/`, {
        headers: legacyHeaders(),
      });
      if (!response.ok)
        throw new Error(
          "Enroll in this program before downloading its workbook.",
        );
      const url = URL.createObjectURL(await response.blob());
      const a = document.createElement("a");
      a.href = url;
      a.download = program.slug + "-workbook.zip";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function downloadKit() {
    setBusy(true);
    try {
      const response = await fetch("/api/learning-kit/", {
        headers: legacyHeaders(),
      });
      if (!response.ok) throw new Error("Sign in again to download the kit.");
      const url = URL.createObjectURL(await response.blob());
      const a = document.createElement("a");
      a.href = url;
      a.download = "practical-ai-learning-kit.zip";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <InterfaceEffects
        viewKey={`${page}:${selected?.id || ""}:${lesson?.id || ""}`}
        contentKey={`${programs.length}:${filter}:${catalogQuery}`}
        title={pageTitle}
      />
      <div className="announcement">
        <Sparkles size={13} /> YOUR NEXT CHAPTER STARTS WITH SOMETHING YOU BUILD{" "}
        <span>
          Explore the academy <ArrowRight size={13} />
        </span>
      </div>
      <header className="header">
        <button
          className="brand"
          onClick={() => navigate("home")}
          aria-label="Practical AI home"
        >
          <span className="brand-mark">
            <Layers3 size={23} />
          </span>
          <span>
            practical<span className="brand-ai">ai</span>
            <small>THE BUILDER’S ACADEMY</small>
          </span>
        </button>
        <nav
          className={menu ? "nav open" : "nav"}
          id="main-navigation"
          aria-label="Main navigation"
        >
          <button
            className={page === "home" ? "active" : ""}
            onClick={goPrograms}
          >
            Programs <ChevronDown size={13} />
          </button>
          <button onClick={() => navigate("accelerator")}>
            GenAI Accelerator <span className="tiny-badge">PROGRAM</span>
          </button>
          <button onClick={() => navigate("terminal")}>Terminal Tutor</button>
          <button onClick={() => navigate("dashboard")}>My learning</button>
        </nav>
        <div className="header-actions">
          {profile ? (
            <>
              <button
                className="icon-button header-search"
                aria-label="Search academy"
                onClick={() => setSearchOpen(true)}
              >
                <Search size={19} />
              </button>
              <button
                className="account-trigger"
                aria-label="Account settings"
                onClick={() => navigate("account")}
              >
                <span>
                  {(profile.display_name || profile.username)
                    .slice(0, 1)
                    .toUpperCase()}
                </span>
                <strong>{profile.display_name || profile.username}</strong>
              </button>
              <button
                className="icon-button"
                aria-label="Sign out"
                onClick={signOut}
              >
                <LogOut size={18} />
              </button>
            </>
          ) : (
            <>
              <button
                className="login"
                onClick={() => {
                  setRegister(false);
                  setAuth(true);
                  setError("");
                }}
              >
                Log in
              </button>
              <button
                className="button small"
                onClick={() => {
                  setRegister(true);
                  setAuth(true);
                  setError("");
                }}
              >
                Start learning <ArrowUpRight size={16} />
              </button>
            </>
          )}
          <button
            className="mobile-toggle icon-button"
            onClick={() => setMenu((current) => !current)}
            aria-label="Toggle navigation"
            aria-expanded={menu}
            aria-controls="main-navigation"
          >
            {menu ? <X /> : <Menu />}
          </button>
        </div>
      </header>
      {error && !auth && (
        <div role="alert" className="error global-error">
          {error}
          <button onClick={() => setError("")} aria-label="Dismiss error">
            <X size={16} />
          </button>
        </div>
      )}
      {page === "home" && (
        <main id="main-content" tabIndex={-1}>
          <section className="hero wrap">
            <div className="hero-copy">
              <div className="eyebrow">
                <span className="live-dot" /> LESS WATCHING. MORE MAKING.
              </div>
              <h1>
                Don’t just learn AI.
                <br />
                Build something
                <br />
                <span>that matters.</span>
                <svg viewBox="0 0 420 20" aria-hidden="true">
                  <path d="M3 14 Q200 -2 414 8" />
                </svg>
              </h1>
              <p>
                Turn your curiosity into real-world skills. Hands-on programs,
                guided projects, and a place to build your next big idea.
              </p>
              <div className="hero-buttons">
                <button className="button" onClick={goPrograms}>
                  Find your program <ArrowUpRight size={18} />
                </button>
                <button
                  className="text-button"
                  onClick={() => navigate("accelerator")}
                >
                  <span className="play-icon">
                    <Play size={12} fill="currentColor" />
                  </span>{" "}
                  Explore the learning lab
                </button>
              </div>
              <div className="hero-note">
                <span className="stacked-icons">
                  <Code2 />
                  <Bot />
                  <Terminal />
                </span>
                <span>
                  Built for curious minds.
                  <br />
                  <strong>
                    Choose a path for your experience. Check each program’s
                    entry skills.
                  </strong>
                </span>
              </div>
            </div>
            <div className="hero-studio">
              <div className="studio-topline">
                <span>
                  <span className="live-dot" /> THE BUILDER’S WORKSPACE
                </span>
                <span>Learn → build → evaluate</span>
              </div>
              <span className="studio-label">A PRACTICAL LEARNING LOOP</span>
              <h2>
                Good ideas need
                <br />
                <em>working evidence.</em>
              </h2>
              <div className="studio-route">
                {[
                  [
                    BookOpen,
                    "01",
                    "Understand the concept",
                    "Step-by-step teaching and complete examples.",
                  ],
                  [
                    Code2,
                    "02",
                    "Build and test it",
                    "Aligned exercises, failure cases and guided labs.",
                  ],
                  [
                    Check,
                    "03",
                    "Show what works",
                    "Evaluation, measured trade-offs and project review.",
                  ],
                ].map(([Icon, n, title, description]) => {
                  const Mark = Icon as typeof BookOpen;
                  return (
                    <div key={String(n)}>
                      <span className="studio-step">
                        <Mark size={20} />
                      </span>
                      <div>
                        <small>{String(n)} / YOUR NEXT STEP</small>
                        <h3>{String(title)}</h3>
                        <p>{String(description)}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="studio-footer">
                <span>Free learning paths</span>
                <span>
                  Private notes & progress <ArrowUpRight size={15} />
                </span>
              </div>
            </div>
          </section>
          <div className="benefit-strip">
            <div className="wrap">
              <span>
                <Code2 /> Project-based, always
              </span>
              <span>
                <BookOpen /> Learn at your own pace
              </span>
              <span>
                <Terminal /> Practice in guided labs
              </span>
              <span>
                <GraduationCap /> Skills you can actually use
              </span>
            </div>
          </div>
          <section id="programs" className="program-section wrap">
            <div className="section-heading">
              <div>
                <div className="eyebrow">FIND YOUR STARTING POINT</div>
                <h2>Choose your next real-world skill.</h2>
                <p>
                  Substantial learning paths. Real artifacts, failure tests, and
                  clear acceptance checks.
                </p>
              </div>
              <span className="section-index">01 — THE PROGRAMS</span>
            </div>
            <div
              className="program-filters"
              role="group"
              aria-label="Filter programs"
            >
              {[
                "All programs",
                "Cohort",
                "Workshop",
                "Masterclass",
                "Accelerator",
                "Engineering",
                "Tutor",
                "Advanced",
              ].map((f) => (
                <button
                  key={f}
                  aria-pressed={filter === f}
                  className={filter === f ? "selected" : ""}
                  onClick={() => setFilter(f)}
                >
                  {f === "Cohort"
                    ? "Bootcamp"
                    : f === "Tutor"
                      ? "Terminal skills"
                      : f}
                </button>
              ))}
              <span>Practical by design. Free to start.</span>
            </div>
            <div className="catalog-search-row">
              <label className="catalog-search">
                <Search size={18} />
                <input
                  type="search"
                  aria-label="Search programs and topics"
                  placeholder="What do you want to build or learn?"
                  value={catalogQuery}
                  onChange={(event) => setCatalogQuery(event.target.value)}
                />
                {catalogQuery && (
                  <button
                    className="icon-button"
                    aria-label="Clear program search"
                    onClick={() => setCatalogQuery("")}
                  >
                    <X size={16} />
                  </button>
                )}
              </label>
              <span role="status">
                {visiblePrograms.length}{" "}
                {visiblePrograms.length === 1 ? "program" : "programs"}
              </span>
            </div>
            {loading ? (
              <div className="empty">
                <LoaderCircle className="spin" /> Loading your next possibility…
              </div>
            ) : programs.length === 0 ? (
              <div className="empty">
                <h3>Programs couldn’t be loaded.</h3>
                <p>
                  Make sure the API is running and the curriculum has been
                  seeded.
                </p>
                <button className="button" onClick={loadPrograms}>
                  Try again
                </button>
              </div>
            ) : visiblePrograms.length === 0 ? (
              <div className="empty catalog-empty">
                <Search size={28} />
                <h3>No programs match that search.</h3>
                <p>
                  Try another topic or reset your filters to explore all
                  programs.
                </p>
                <button
                  className="button secondary"
                  onClick={() => {
                    setCatalogQuery("");
                    setFilter("All programs");
                  }}
                >
                  Reset program filters
                </button>
              </div>
            ) : (
              <div className="program-grid">
                {visiblePrograms.map((p) => {
                  const index = catalogPrograms.indexOf(p);
                  const Icon =
                    p.category === "Tutor" ? Terminal : icons[index % 4];
                  return (
                    <article
                      key={p.id}
                      className={`program-card tone-${index}`}
                    >
                      <div className="program-art">
                        <div className="program-pattern" />
                        <span className="category">
                          {p.category === "Cohort"
                            ? "THE DEEP DIVE"
                            : p.category === "Workshop"
                              ? "THE BUILD STUDIOS"
                              : p.category === "Accelerator"
                                ? "THE ACCELERATOR"
                                : p.category === "Engineering"
                                  ? "THE ENGINEERING PATH"
                                  : p.category === "Tutor"
                                    ? "THE COMMAND LINE"
                                    : p.category === "Advanced" ? "ADVANCED PYTHON" : "THE CLIENT PRACTICUM"}
                        </span>
                        <Icon className="program-main-icon" strokeWidth={1.1} />
                        <span className="art-number">0{index + 1}</span>
                        <div className="art-tag">
                          {p.category === "Cohort"
                            ? "IDEA → AGENT"
                            : p.category === "Workshop"
                              ? "LEARN. MAKE. REPEAT."
                              : p.category === "Accelerator"
                                ? "FOUNDATIONS → CAPSTONE"
                                : p.category === "Engineering"
                                  ? "SOFTWARE → PRODUCTION"
                                  : p.category === "Tutor"
                                    ? "PRACTICE → CONFIDENCE"
                                    : p.category === "Advanced" ? "PYTHON → AI SERVICES" : "SKILLS → OPPORTUNITY"}
                        </div>
                      </div>
                      <div className="program-content">
                        <div className="program-meta">
                          <span>
                            <Clock3 size={13} />
                            {p.duration}
                          </span>
                          <span>{p.category}</span>
                        </div>
                        <h3>{p.title}</h3>
                        <p>{p.description}</p>
                        <div className="outcome">
                          <span>YOU’LL WALK AWAY WITH</span>
                          <p>{p.outcome}</p>
                        </div>
                        <details className="program-syllabus">
                          <summary>
                            {p.lessons.length} practical sessions · view
                            syllabus
                          </summary>
                          <p>
                            About{" "}
                            {Math.round(
                              p.lessons.reduce((n, l) => n + l.minutes, 0) / 60,
                            )}{" "}
                            hours of reading, building, testing, and review.
                            Self-paced; suggested schedule shown above.
                          </p>
                          <ol>
                            {[...new Set(p.lessons.map((l) => l.module))].map(
                              (module) => (
                                <li key={module}>{module}</li>
                              ),
                            )}
                          </ol>
                          <p>{p.level}</p>
                        </details>
                        <button
                          disabled={busy}
                          onClick={() => viewProgram(p)}
                          className="program-link"
                        >
                          Explore program <ArrowUpRight size={19} />
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
            <div className="catalog-note">
              <CircleCheck size={15} />
              <span>
                Seven independent learning paths. Choose your starting point,
                build the evidence.
              </span>
            </div>
          </section>
          <section className="lab-section">
            <div className="wrap">
              <div className="section-heading">
                <div>
                  <div className="eyebrow">A LITTLE HELP GOES A LONG WAY</div>
                  <h2>An independent path. A place to practice.</h2>
                  <p>
                    The GenAI Accelerator has its own curriculum and capstone.
                    Terminal Tutor is a separate practice companion.
                  </p>
                </div>
                <span className="section-index">02 — EXPLORE FURTHER</span>
              </div>
              <div className="labs-grid">
                <article className="lab-card">
                  <div className="lab-card-heading">
                    <span className="card-icon">
                      <Sparkles />
                    </span>
                    <span className="outline-badge">INDEPENDENT PROGRAM</span>
                  </div>
                  <h3>GenAI Accelerator</h3>
                  <p>
                    Study foundations, RAG, evaluation, deployment, agents and
                    MCP with complete examples, aligned practice and diagnostic
                    feedback. Includes an independent capstone starter.
                  </p>
                  <button
                    className="text-button"
                    onClick={() => navigate("accelerator")}
                  >
                    Open the Accelerator <ArrowUpRight size={17} />
                  </button>
                  <div className="mini-workflow">
                    <span>
                      <Sparkles size={15} /> Your idea
                    </span>
                    <ArrowRight size={16} />
                    <span>
                      <Layers3 size={15} /> A clear plan
                    </span>
                    <ArrowRight size={16} />
                    <span>
                      <Rocket size={15} /> First build
                    </span>
                  </div>
                </article>
                <article className="lab-card terminal-card">
                  <div className="lab-card-heading">
                    <span className="card-icon">
                      <Terminal />
                    </span>
                    <span className="outline-badge">SAFE PRACTICE SPACE</span>
                  </div>
                  <h3>Meet your Terminal Tutor.</h3>
                  <p>
                    Learn workspace isolation, process exits, debugging, tool
                    boundaries and session recall through eight complete guided
                    lessons. Try basic commands in the separate simulation.
                  </p>
                  <button
                    className="text-button"
                    onClick={() => navigate("terminal")}
                  >
                    Try your first command <ArrowUpRight size={17} />
                  </button>
                  <div className="mini-terminal">
                    <span>learner@practical-ai ~</span>
                    <br />❯ pwd <span className="cursor" />
                  </div>
                </article>
              </div>
            </div>
          </section>
          <section className="how-section wrap">
            <div>
              <div className="eyebrow">PROGRESS OVER PERFECTION</div>
              <h2>
                You don’t need to
                <br />
                have it all figured out.
              </h2>
              <p>
                Bring a little curiosity. We’ll help you turn it into something
                useful, one step at a time.
              </p>
              <button className="button" onClick={goPrograms}>
                Let’s build something <ArrowUpRight size={17} />
              </button>
            </div>
            <div className="steps">
              {[
                [
                  "01",
                  "Find your path",
                  "Choose a program that fits your starting point and what you want to make.",
                ],
                [
                  "02",
                  "Learn by doing",
                  "Work through substantial lessons, complete implementations, and test failure cases.",
                ],
                [
                  "03",
                  "Make it yours",
                  "Build a useful project and leave with something you can show, share, and improve.",
                ],
              ].map(([n, title, desc]) => (
                <div className="step" key={n}>
                  <span>{n}</span>
                  <div>
                    <h3>{title}</h3>
                    <p>{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
          <section className="faq-section wrap">
            <div className="eyebrow">A FEW THINGS YOU MIGHT BE WONDERING</div>
            <h2>Curiosity looks good on you.</h2>
            {[
              [
                "Do I need a technical background?",
                "Python for AI is advanced: it expects existing Python, HTTP/JSON, testing and basic SQL skills. AI Engineering expects Python, HTTP/JSON, SQL and Git basics. No prior model training is required. Bootcamp includes setup but expects willingness to practice Python and HTTP basics. Workshops offer six substantial project studios. Freelancing starts from one working workflow. Each path includes implementation, review, and deliverables; expect sustained practice.",
              ],
              [
                "Is the academy free?",
                "Yes. All programs, the full workshop library, the GenAI Accelerator, and Terminal Tutor are free for this first release. Create an account to save your learning progress. Optional provider calls, cloud hosting and GPU experiments use your own accounts and may incur charges.",
              ],
              [
                "What will I actually build?",
                "Bootcamp: a tested support agent with citations, permissioned tools, evaluation, and deployment. Workshops: six workflows covering extraction, meetings, research, triage, content operations, and an integrated app. AI Engineering: five capstones across real-time voice, mixed-media RAG, workspace agents, LLMOps and a measured hybrid SaaS release. Freelancing: a complete simulated client engagement from discovery and scope to evaluation and handover. Python for AI: a bounded, authenticated knowledge service with async workers, owner-scoped context, persistent caching, evaluation and a Docker runbook.",
              ],
              [
                "Are the learning tools connected to an AI model?",
                "The original Accelerator lessons, labs, and capstone starter are included, alongside the Terminal Tutor guide and full source library. The project planner is a guided template and the terminal is simulated. No paid model calls are made.",
              ],
            ].map(([q, a], i) => (
              <div className="faq-item" key={q}>
                <button
                  aria-expanded={faq === i}
                  onClick={() => setFaq(faq === i ? null : i)}
                >
                  {q}
                  <ChevronDown
                    size={18}
                    className={faq === i ? "rotate" : ""}
                  />
                </button>
                {faq === i && <p>{a}</p>}
              </div>
            ))}
          </section>
          <section className="bottom-cta wrap">
            <div className="eyebrow">YOUR “SOMEDAY” CAN START TODAY</div>
            <h2>
              A small first step.
              <br />A whole new set of possibilities.
            </h2>
            <button className="button" onClick={goPrograms}>
              Find your starting point <ArrowUpRight size={18} />
            </button>
            <span>Free to learn. Yours to build.</span>
            <Sparkles className="cta-spark" />
          </section>
        </main>
      )}
      {page === "preview" && selected && (
        <Suspense
          fallback={
            <div className="workspace-loading wrap" role="status">
              <LoaderCircle className="spin" size={18} />
              Opening the lesson preview…
            </div>
          }
        >
          <PreviewLesson
            key={selected.id}
            program={selected}
            onStart={() => openProgram(selected)}
            onBack={() => viewProgram(selected)}
          />
        </Suspense>
      )}
      {page === "course" && selected && (
        <CourseOverview
          program={selected}
          profile={profile}
          onBack={goPrograms}
          onPreview={() => {
            setPage("preview");
            window.scrollTo(0, 0);
          }}
          onStart={() => openProgram(selected)}
          busy={busy}
        />
      )}
      {page !== "home" && page !== "course" && page !== "preview" && (
        <main id="main-content" tabIndex={-1} className={`workspace wrap ${page === "learn" ? "course-workspace" : ""}`}>
          <nav className="workspace-nav" aria-label="Workspace">
            <span className="eyebrow rail-label">YOUR WORKSPACE</span>
            {(
              [
                ["dashboard", "My learning", LayoutDashboard],
                ["portfolio", "Project portfolio", FolderCheck],
                ["accelerator", "GenAI Accelerator", Sparkles],
                ["terminal", "Terminal Tutor", Terminal],
                ["account", "Account settings", UserRound],
              ] as const
            ).map(([p, label, Icon]) => (
              <button
                key={p}
                className={page === p ? "selected" : ""}
                aria-current={page === p ? "page" : undefined}
                onClick={() => navigate(p)}
              >
                <Icon size={18} />
                {label}
              </button>
            ))}
            <button className="rail-search" onClick={() => setSearchOpen(true)}>
              <Search size={18} />
              Search lessons<kbd>⌘ K</kbd>
            </button>
            <div className="rail-note">
              <BookOpen size={23} />
              <strong>Build a little today.</strong>
              <p>Your next lesson is waiting.</p>
              <button className="text-button" onClick={goPrograms}>
                Explore all programs
                <ArrowRight size={14} />
              </button>
            </div>
          </nav>
          <div className="workspace-body">
            <Suspense
              fallback={
                <div className="workspace-loading" role="status">
                  <LoaderCircle className="spin" size={18} />
                  Opening your workspace…
                </div>
              }
            >
              {page === "account" && (
                <AccountSettings onUpdated={() => void refresh()} />
              )}
              {page === "portfolio" && <StudentPortfolio />}
              {page === "dashboard" && (
                <>
                  {profile && (
                    <StudyDashboard
                      profile={profile}
                      programs={programs}
                      onLesson={openLesson}
                      onExplore={goPrograms}
                    />
                  )}{" "}
                  {profile && (
                    <LearningHub
                      profile={profile}
                      programs={programs}
                      onOpen={viewProgram}
                      onLesson={openLesson}
                    />
                  )}
                  <h2>Your learning paths</h2>
                  <div className="dashboard-courses">
                    {programs
                      .filter((p) => p.category !== "Library")
                      .map((p) => {
                        const enrolled = profile?.enrolled.includes(p.id);
                        const count = p.lessons.filter((l) =>
                          profile?.completed.includes(l.id),
                        ).length;
                        return (
                          <article className="dashboard-course" key={p.id}>
                            <div>
                              <span className="eyebrow">
                                {p.category} · {p.duration}
                              </span>
                              <h3>{p.title}</h3>
                              <p>{p.outcome}</p>
                              <button
                                className="text-button syllabus-link"
                                onClick={() => viewProgram(p)}
                              >
                                View program syllabus <ArrowUpRight size={13} />
                              </button>
                              {enrolled && (
                                <>
                                  <progress
                                    value={count}
                                    max={p.lessons.length}
                                  />
                                  <small>
                                    {count} of {p.lessons.length} lessons marked
                                    read
                                  </small>
                                </>
                              )}
                            </div>
                            <button
                              className="button"
                              disabled={busy}
                              onClick={() => openProgram(p)}
                            >
                              {enrolled ? "Continue learning" : "Join for free"}
                              <ArrowRight size={16} />
                            </button>
                          </article>
                        );
                      })}
                  </div>
                  <section className="source-library">
                    <div className="eyebrow">THE FULL WORKSHOP LIBRARY</div>
                    <h2>523 chapters. Follow your curiosity.</h2>
                    <p className="muted">
                      20 phases from setup and machine learning to agent
                      engineering. Pinned source readings, examples, and
                      original quizzes.
                    </p>
                    <input
                      aria-label="Search learning paths"
                      placeholder="Find a phase, topic, or lesson…"
                      value={librarySearch}
                      onChange={(e) => setLibrarySearch(e.target.value)}
                    />
                    <div className="library-grid">
                      {programs
                        .filter(
                          (p) =>
                            p.category === "Library" &&
                            (
                              p.title +
                              " " +
                              p.lessons.map((l) => l.title).join(" ")
                            )
                              .toLowerCase()
                              .includes(librarySearch.toLowerCase()),
                        )
                        .map((p) => (
                          <button
                            key={p.id}
                            onClick={() => openProgram(p)}
                            disabled={busy}
                          >
                            <BookOpen size={19} />
                            <span>
                              <strong>{p.title}</strong>
                              <small>{p.duration}</small>
                            </span>
                            <ArrowUpRight size={16} />
                          </button>
                        ))}
                    </div>
                    <button
                      className="text-button download-kit"
                      disabled={busy}
                      onClick={downloadKit}
                    >
                      Download curriculum + capstone learning kit{" "}
                      <ArrowUpRight size={17} />
                    </button>
                  </section>
                </>
              )}
              {page === "learn" && selected && lesson && (
                <>
                  <CourseModuleNav program={selected} lesson={lesson} onLesson={id => openLesson(selected, id)}/>
                  <div className="learning-heading">
                    <button
                      className="text-button"
                      onClick={() => viewProgram(selected)}
                    >
                      <BookOpen size={14} />
                      {selected.title} · syllabus
                    </button>
                    <span>
                      {
                        selected.lessons.filter((l) =>
                          profile?.completed.includes(l.id),
                        ).length
                      }
                      /{selected.lessons.length} lessons marked read
                    </span>
                  </div>
                  <div className="lesson-layout">
                    <CourseNavigation key={selected.id} program={selected} lesson={lesson} completed={profile?.completed || []} query={lessonSearch} onQuery={setLessonSearch} onLesson={id => openLesson(selected, id)}/>
                    <article className="lesson-content">
                      <div className="eyebrow">
                        {lesson.module} · ~{lesson.minutes} PRACTICE MIN
                      </div>
                      <h1>{lesson.title}</h1>
                      {!lesson.resources?.learning && (
                        <div className="lesson-illustration">
                          <BookOpen size={35} />
                          <span>
                            {selected.title}
                            <br />
                            <strong>
                              Concept chapters. Worked implementations.
                              Deliberate practice.
                            </strong>
                          </span>
                        </div>
                      )}
                      <LessonReader
                        lesson={lesson}
                        loading={lessonLoading}
                        onError={setError}
                        onDownloadKit={() => downloadProgram(selected)}
                      />
                      {!lesson.resources?.learning && (
                        <div className="exercise">
                          <span className="eyebrow">
                            <Code2 size={16} /> YOUR TURN
                          </span>
                          <h3>Put it into practice.</h3>
                          <p>{lesson.task}</p>
                        </div>
                      )}
                      <div
                        className="lesson-evidence-status"
                        aria-label="Lesson evidence"
                      >
                        <span>
                          Reading:{" "}
                          {profile?.completed.includes(lesson.id)
                            ? "marked read"
                            : "not marked read"}
                        </span>
                        <span>
                          Quiz:{" "}
                          {profile?.progress.quiz_passed.includes(lesson.id)
                            ? "all questions correct"
                            : "not yet passed"}
                        </span>
                        {lesson.lab && (
                          <span>
                            Browser checks:{" "}
                            {profile?.progress.lab_passed.includes(lesson.id)
                              ? "passed · browser-reported"
                              : "not yet passed"}
                          </span>
                        )}
                        <span>
                          Project review:{" "}
                          {profile?.progress.reviewed.includes(lesson.id)
                            ? "reviewed"
                            : "not yet reviewed"}
                        </span>
                      </div>
                      <div className="lesson-actions">
                        <button
                          className="button secondary"
                          disabled={busy}
                          aria-pressed={
                            !!lesson && bookmarks.includes(lesson.id)
                          }
                          onClick={toggleBookmark}
                        >
                          <Bookmark size={17} />
                          {bookmarks.includes(lesson.id)
                            ? "Saved lesson"
                            : "Save lesson"}
                        </button>
                        <button
                          className="button"
                          disabled={busy || lessonLoading}
                          onClick={toggleComplete}
                        >
                          <Check size={17} />
                          {profile?.completed.includes(lesson.id)
                            ? "Read · mark unread"
                            : "Mark lesson read"}
                        </button>
                        {selected.lessons.findIndex((l) => l.id === lesson.id) <
                          selected.lessons.length - 1 && (
                          <button
                            className="text-button"
                            onClick={() =>
                              openLesson(
                                selected,
                                selected.lessons[
                                  selected.lessons.findIndex(
                                    (l) => l.id === lesson.id,
                                  ) + 1
                                ].id,
                              )
                            }
                          >
                            Next lesson <ArrowRight size={16} />
                          </button>
                        )}
                      </div>
                    </article>
                  </div>
                </>
              )}
              {page === "accelerator" && (
                <>
                  <div className="eyebrow">YOUR INDEPENDENT PROGRAM</div>
                  <h1 className="workspace-title">Your GenAI Accelerator.</h1>
                  <p className="muted">
                    A self-contained program with its own lessons, labs and
                    capstone. Enroll independently and work at your own pace.
                  </p>
                  <div className="course-banner">
                    <div>
                      <span className="eyebrow">
                        THE ORIGINAL WORKSHOP PATH
                      </span>
                      <h2>
                        {acceleratorProgram?.lessons.length || 105} lessons &
                        labs. One useful capstone.
                      </h2>
                      <p>
                        Core foundations plus advanced agent loops, graph
                        orchestration, multi-agent contracts, and MCP. Work at
                        your own pace.
                      </p>
                    </div>
                    <div>
                      <button
                        className="button"
                        disabled={!acceleratorProgram || busy}
                        onClick={() =>
                          acceleratorProgram && openProgram(acceleratorProgram)
                        }
                      >
                        Open curriculum <ArrowRight size={17} />
                      </button>
                      <button
                        className="text-button"
                        disabled={busy || !acceleratorProgram}
                        onClick={() =>
                          acceleratorProgram &&
                          downloadProgram(acceleratorProgram)
                        }
                      >
                        Download starter kit <ArrowUpRight size={16} />
                      </button>
                    </div>
                  </div>
                  <div className="accelerator-layout">
                    <div>
                      <form className="panel" onSubmit={createProject}>
                        <Sparkles className="accent" />
                        <h2>Plan a project of your own.</h2>
                        <p className="planner-note">
                          Guided template · no AI generation or paid model
                          calls.
                        </p>
                        <label>
                          Project name
                          <input
                            name="title"
                            required
                            maxLength={150}
                            placeholder="e.g. My research assistant"
                          />
                        </label>
                        <label>
                          The problem you want to solve
                          <textarea
                            name="problem"
                            required
                            maxLength={3000}
                            rows={5}
                            placeholder="Who is this for? What task should it help with? What would a useful result look like?"
                          />
                        </label>
                        <button className="button" disabled={busy}>
                          {busy ? "Creating…" : "Create my project plan"}
                          <ArrowUpRight size={17} />
                        </button>
                      </form>
                      <div className="saved-projects">
                        <h3>Your saved projects</h3>
                        {projects.length === 0 ? (
                          <p className="muted">
                            Your first project could start right here.
                          </p>
                        ) : (
                          projects.map((p) => (
                            <button
                              key={p.id}
                              onClick={() => setActiveProject(p)}
                              className={
                                activeProject?.id === p.id ? "selected" : ""
                              }
                            >
                              <Layers3 size={16} />
                              {p.title}
                              <ArrowRight size={15} />
                            </button>
                          ))
                        )}
                      </div>
                    </div>
                    <div className="panel blueprint">
                      {activeProject ? (
                        <>
                          <span className="eyebrow">YOUR BUILD BLUEPRINT</span>
                          <h2>{activeProject.title}</h2>
                          <p>{activeProject.problem}</p>
                          <ol>
                            {activeProject.blueprint.steps.map((s, i) => (
                              <li key={s}>
                                <span>{i + 1}</span>
                                {s}
                              </li>
                            ))}
                          </ol>
                          <h3>What you’ll deliver</h3>
                          <div className="deliverables">
                            {activeProject.blueprint.deliverables.map((d) => (
                              <span key={d}>
                                <Check size={14} />
                                {d}
                              </span>
                            ))}
                          </div>
                          <button
                            className="text-button"
                            onClick={() => {
                              const blob = new Blob(
                                [JSON.stringify(activeProject, null, 2)],
                                { type: "application/json" },
                              );
                              const url = URL.createObjectURL(blob);
                              const a = document.createElement("a");
                              a.href = url;
                              a.download = "project-blueprint.json";
                              a.click();
                              URL.revokeObjectURL(url);
                            }}
                          >
                            Download your blueprint <ArrowUpRight size={16} />
                          </button>
                        </>
                      ) : (
                        <div className="blueprint-empty">
                          <Layers3 size={55} />
                          <h2>From possibility to a plan.</h2>
                          <p>
                            Describe your idea and your build checklist will
                            appear here.
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </>
              )}
              {page === "terminal" && (
                <>
                  <div className="eyebrow">
                    MAKE FRIENDS WITH THE COMMAND LINE
                  </div>
                  <h1 className="workspace-title">
                    A safe space to try things.
                  </h1>
                  <p className="muted">
                    A simulated terminal with guided feedback. Commands never
                    run on your computer.
                  </p>
                  <div className="course-banner">
                    <div>
                      <span className="eyebrow">
                        YOUR ORIGINAL TERMINAL TUTOR
                      </span>
                      <h2>Learn. Code. Run. Review.</h2>
                      <p>
                        Eight guided lessons with step-by-step teaching,
                        runnable examples, quizzes, flashcards and diagnostic
                        feedback.
                      </p>
                    </div>
                    <div>
                      <button
                        className="button"
                        disabled={!terminalProgram || busy}
                        onClick={() =>
                          terminalProgram && openProgram(terminalProgram)
                        }
                      >
                        Open the tutor lessons <ArrowRight size={17} />
                      </button>
                      <button
                        className="text-button"
                        disabled={busy}
                        onClick={downloadKit}
                      >
                        Download learning kit <ArrowUpRight size={16} />
                      </button>
                    </div>
                  </div>
                  <div className="terminal-layout">
                    <div className="terminal-shell">
                      <div className="window-bar">
                        <div className="window-dots">
                          <i />
                          <i />
                          <i />
                        </div>
                        <span>learner@practical-ai — simulation</span>
                        <button
                          onClick={() =>
                            setTerminalLines([
                              "Terminal cleared. Type help to start again.",
                            ])
                          }
                        >
                          Clear
                        </button>
                      </div>
                      <pre
                        ref={terminalOutput}
                        role="log"
                        aria-label="Terminal output"
                        aria-live="polite"
                      >
                        {terminalLines.join("\n\n")}
                        {terminalBusy ? "\n\nWorking…" : ""}
                      </pre>
                      <form onSubmit={runCommand}>
                        <label htmlFor="command">❯</label>
                        <input
                          id="command"
                          value={command}
                          onChange={(e) => {
                            setCommand(e.target.value);
                            setHistoryIndex(-1);
                          }}
                          onKeyDown={(event) => {
                            if (
                              !["ArrowUp", "ArrowDown"].includes(event.key) ||
                              !commandHistory.length ||
                              (event.key === "ArrowDown" && historyIndex === -1)
                            )
                              return;
                            event.preventDefault();
                            if (historyIndex === -1) setCommandDraft(command);
                            const next =
                              event.key === "ArrowUp"
                                ? Math.min(
                                    historyIndex + 1,
                                    commandHistory.length - 1,
                                  )
                                : Math.max(historyIndex - 1, -1);
                            setHistoryIndex(next);
                            setCommand(
                              next === -1 ? commandDraft : commandHistory[next],
                            );
                          }}
                          aria-describedby="command-history-help"
                          placeholder="Type a command…"
                          autoComplete="off"
                          spellCheck={false}
                          maxLength={200}
                        />
                        <button
                          disabled={terminalBusy || !command.trim()}
                          aria-label="Run command"
                        >
                          <ArrowRight size={19} />
                        </button>
                      </form>
                      <p
                        id="command-history-help"
                        className="command-history-help"
                      >
                        ↑ ↓ recall commands · Enter to run · simulated workspace
                      </p>
                    </div>
                    <aside className="panel">
                      <Terminal className="accent" />
                      <h3>Your first five commands</h3>
                      <p className="muted">
                        Try these in order. Read the feedback after each
                        command.
                      </p>
                      {[
                        ["pwd", "Find out where you are"],
                        ["ls", "See what’s in your folder"],
                        ["cat README.md", "Read a project file"],
                        ["mkdir my-agent", "Practice creating a folder"],
                        ["python --version", "Check your Python version"],
                      ].map(([c, d]) => (
                        <button
                          className="command-example"
                          key={c}
                          onClick={() => setCommand(c)}
                        >
                          <code>{c}</code>
                          <span>{d}</span>
                        </button>
                      ))}
                      <small>
                        This is a stateless command tutorial. Files and folders
                        are illustrative.
                      </small>
                    </aside>
                  </div>
                </>
              )}
            </Suspense>
          </div>
        </main>
      )}
      <footer className="footer wrap">
        <button className="brand" onClick={() => navigate("home")}>
          <span className="brand-mark">
            <Layers3 size={20} />
          </span>
          <span>
            practical<span className="brand-ai">ai</span>
          </span>
        </button>
        <span>A little curiosity. A lot of possibility.</span>
        <small>© {new Date().getFullYear()} Practical AI Education</small>
      </footer>
      {recovery && (
        <PasswordRecovery
          uid={recovery.uid}
          token={recovery.token}
          onClose={() => {
            setRecovery(null);
            history.replaceState(null, "", "#/");
          }}
          onLogin={() => {
            setRecovery(null);
            history.replaceState(null, "", "#/");
            setRegister(false);
            setAuth(true);
          }}
        />
      )}
      {auth && !recovery && (
        <AuthDialog
          register={register}
          busy={busy}
          error={error}
          onClose={() => {
            setAuth(false);
            setError("");
            setPendingProgram(null);
            setPendingRoute("");
          }}
          onSwitch={() => {
            setRegister(!register);
            setError("");
          }}
          onRecovery={() => {
            setAuth(false);
            setRecovery({});
          }}
          onSubmit={submitAuth}
        />
      )}
      {searchOpen && profile && (
        <Suspense fallback={null}>
          <SearchDialog
            onClose={() => setSearchOpen(false)}
            onOpen={openSearchHit}
          />
        </Suspense>
      )}
    </>
  );
}
