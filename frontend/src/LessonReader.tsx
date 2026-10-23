import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ArrowUpRight, LoaderCircle } from "lucide-react";
import LearningStudio from "./LearningStudio";
import EngineeringContract from "./EngineeringContract";
import useNotes from "./useNotes";
import type { Lesson, Learning, ModulePedagogy } from "./types";
export default function LessonReader({
  lesson,
  loading,
  onError,
  onDownloadKit,
}: {
  lesson: Lesson;
  loading: boolean;
  onError: (error: string) => void;
  onDownloadKit: () => Promise<void>;
}) {
  const content = lesson.content?.startsWith("# " + lesson.title + "\n")
    ? lesson.content.slice(lesson.title.length + 3).trimStart()
    : lesson.content;
  if (loading)
    return (
      <div className="flex items-center gap-3 py-10 text-brand" role="status">
        <LoaderCircle className="spin" size={18} /> Opening your reading…
      </div>
    );
  const learning = lesson.resources?.learning as Learning | undefined;
  if (learning)
    return (
      <LearningStudio
        key={lesson.id}
        lesson={lesson}
        learning={learning}
        content={content}
        onError={onError}
      />
    );
  return (
    <>
      {lesson.resources?.pedagogy ? (
        <EngineeringContract
          contract={lesson.resources.pedagogy as ModulePedagogy}
        />
      ) : null}
      {lesson.source_id && (
        <div className="source-note">
          <span>
            {lesson.source_id.startsWith("academy-v2:")
              ? "Practical academy program"
              : "Workshop source"}{" "}
            · {lesson.source_id.split(":").pop()}
          </span>
          {lesson.source_url && (
            <a href={lesson.source_url} target="_blank" rel="noreferrer">
              View source <ArrowUpRight size={12} />
            </a>
          )}
        </div>
      )}
      {lesson.source_id?.startsWith("academy-v2:") && (
        <div className="practical-brief">
          <span className="eyebrow">BUILD · TEST · EXPLAIN</span>
          <p>
            <strong>Your artifact:</strong>{" "}
            <code>{String(lesson.resources?.artifact || "")}</code>
          </p>
          <p>
            <strong>Program capstone:</strong>{" "}
            {String(lesson.resources?.capstone || "")}
          </p>
          <button className="text-button" onClick={onDownloadKit}>
            Download offline labs & worksheets <ArrowUpRight size={14} />
          </button>
          <small>
            Run exercises in a separate local workspace. No code runs inside
            this lesson reader.
          </small>
        </div>
      )}
      <div className="markdown-reader">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          skipHtml
          components={{
            img: () => (
              <span className="blocked-image">
                [Illustration omitted from imported source]
              </span>
            ),
            a: ({ href, children }) => (
              <a href={href} target="_blank" rel="noreferrer">
                {children}
              </a>
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
      {lesson.resources &&
        ["code", "quiz"].map((key) =>
          lesson.resources?.[key] ? (
            <details className="source-artifact" key={key}>
              <summary>
                {key === "code"
                  ? "Original source code references"
                  : "Original source quiz & answer reference"}
              </summary>
              <pre>
                {typeof lesson.resources[key] === "string"
                  ? (lesson.resources[key] as string)
                  : JSON.stringify(lesson.resources[key], null, 2)}
              </pre>
            </details>
          ) : null,
        )}
      <LegacyNotebook key={lesson.id} lesson={lesson} />
    </>
  );
}

function LegacyNotebook({ lesson }: { lesson: Lesson }) {
  const notebook = useNotes(lesson.id, lesson.notes || "");
  return (
    <div className="learner-notes">
      <label>
        Your notes & observations
        <textarea
          rows={5}
          aria-label="Your notes & observations"
          value={notebook.notes}
          onChange={(event) => notebook.edit(event.target.value)}
          maxLength={10000}
        />
      </label>
      <small role="status">{notebook.message}</small>
      <button
        className="text-button"
        onClick={() => void notebook.save()}
        disabled={notebook.saving}
      >
        Save notes
      </button><button className="text-button" onClick={notebook.exportDraft}>Export notes or recovery draft</button>{notebook.blocked&&<button className="text-button" onClick={()=>void notebook.loadAccount()}>Load account notes and retain browser backup</button>}
    </div>
  );
}
