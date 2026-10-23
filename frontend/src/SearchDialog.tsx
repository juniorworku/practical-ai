import { useEffect, useRef, useState } from "react";
import { ArrowUpRight, BookOpen, Search, X } from "lucide-react";
import { api } from "./api";
export type SearchHit = {
  lesson: number;
  program: string;
  program_title: string;
  title: string;
  module: string;
  snippet: string;
  match: string;
};
export default function SearchDialog({
  onClose,
  onOpen,
}: {
  onClose: () => void;
  onOpen: (hit: SearchHit) => void;
}) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchHit[]>([]);
  const [status, setStatus] = useState(
    "Search your enrolled lessons, concepts and private notes.",
  );
  const [busy, setBusy] = useState(false);
  const dialog = useRef<HTMLElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    dialog.current?.querySelector("input")?.focus();
    const key = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
      if (event.key === "Tab") {
        const nodes = [
          ...(dialog.current?.querySelectorAll<HTMLElement>("input,button") ||
            []),
        ];
        if (event.shiftKey && document.activeElement === nodes[0]) {
          event.preventDefault();
          nodes.at(-1)?.focus();
        } else if (!event.shiftKey && document.activeElement === nodes.at(-1)) {
          event.preventDefault();
          nodes[0]?.focus();
        }
      }
    };
    window.addEventListener("keydown", key);
    return () => {
      window.removeEventListener("keydown", key);
      document.body.style.overflow = overflow;
      previous?.focus();
    };
  }, [onClose]);
  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([]);
      setBusy(false);
      setStatus(
        "Type at least two characters. Only your enrolled programs and notes are searched.",
      );
      return;
    }
    let alive = true;
    const controller = new AbortController();
    setResults([]);
    setBusy(true);
    const timer = window.setTimeout(() => {
      api<SearchHit[]>(`search/?q=${encodeURIComponent(query.trim())}`, {
        signal: controller.signal,
      })
        .then((data) => {
          if (alive) {
            setResults(data);
            setStatus(
              data.length
                ? `${data.length} results`
                : "No matches. Try a concept, lesson title or a phrase from your notes.",
            );
          }
        })
        .catch((error) => {
          if (alive) setStatus(error.message);
        })
        .finally(() => {
          if (alive) setBusy(false);
        });
    }, 250);
    return () => {
      alive = false;
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [query]);
  return (
    <div
      className="modal-backdrop"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        ref={dialog}
        className="search-dialog"
        role="dialog"
        aria-modal="true"
        aria-label="Search learning workspace"
      >
        <div className="search-input-row">
          <Search size={21} />
          <input
            aria-label="Search lessons and notes"
            placeholder="Search a concept, lesson or note…"
            value={query}
            maxLength={100}
            onKeyDown={(event) => {
              if (event.key === "ArrowDown") {
                event.preventDefault();
                dialog.current
                  ?.querySelector<HTMLButtonElement>(".search-results button")
                  ?.focus();
              }
              if (event.key === "Enter" && !busy && results[0]) {
                event.preventDefault();
                onOpen(results[0]);
              }
            }}
            onChange={(event) => setQuery(event.target.value)}
          />
          <button
            className="icon-button"
            aria-label="Close search"
            onClick={onClose}
          >
            <X size={19} />
          </button>
        </div>
        <p role="status">{busy ? "Searching…" : status}</p>
        <small className="search-keyboard-help">
          Enter opens the first result · ↓ and Tab browse results · Esc closes
        </small>
        <div
          aria-busy={busy}
          className="search-results"
          onKeyDown={(event) => {
            if (!["ArrowDown", "ArrowUp"].includes(event.key)) return;
            const buttons = [
              ...event.currentTarget.querySelectorAll<HTMLButtonElement>(
                "button",
              ),
            ];
            const index = buttons.indexOf(
              document.activeElement as HTMLButtonElement,
            );
            event.preventDefault();
            if (event.key === "ArrowUp" && index <= 0)
              dialog.current?.querySelector("input")?.focus();
            else
              buttons[
                Math.min(
                  buttons.length - 1,
                  event.key === "ArrowDown" ? index + 1 : index - 1,
                )
              ]?.focus();
          }}
        >
          {results.map((hit) => (
            <button key={hit.lesson} onClick={() => onOpen(hit)}>
              <BookOpen size={19} />
              <div>
                <small>
                  {hit.program_title} · {hit.match}
                </small>
                <strong>{hit.title}</strong>
                <p>{hit.snippet}</p>
              </div>
              <ArrowUpRight size={16} />
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
