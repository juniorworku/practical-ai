import { useState } from "react";
import { api } from "./api";
import { TeachingMarkdown } from "./ConceptReader";
type SourceFile = { path: string; content: string };
export default function CapstoneFiles({ slug }: { slug: string }) {
  const [files, setFiles] = useState<SourceFile[]>([]);
  const [selected, setSelected] = useState(0);
  const [status, setStatus] = useState("");
  const [loaded, setLoaded] = useState(false);
  const active = files[selected];
  return (
    <details className="capstone-files">
      <summary>Browse the reference capstone files</summary>
      <p>
        Compare after your own attempt. These are the program’s authored
        reference files, not your submitted project or proof that your
        deployment works.
      </p>
      {!loaded && (
        <button
          className="text-button"
          onClick={async () => {
            try {
              setFiles(
                await api<SourceFile[]>(`programs/${slug}/capstone-files/`),
              );
              setLoaded(true);
            } catch (error) {
              setStatus((error as Error).message);
            }
          }}
        >
          Load reference files
        </button>
      )}
      {loaded && !files.length && (
        <p>
          This program has no separate multi-file reference bundle. Use its
          inline worked implementation.
        </p>
      )}
      {files.length > 0 && (
        <>
          <div className="file-tabs" role="group" aria-label="Reference files">
            {files.map((file, index) => (
              <button
                className="text-button"
                aria-pressed={selected === index}
                key={file.path}
                onClick={() => setSelected(index)}
              >
                {file.path}
              </button>
            ))}
          </div>
          <h3>{active.path}</h3>
          <TeachingMarkdown>
            {active.path.endsWith(".md")
              ? active.content
              : "```" +
                (active.path.endsWith(".py") ? "python" : "text") +
                "\n" +
                active.content +
                "\n```"}
          </TeachingMarkdown>
        </>
      )}
      <p role="status">{status}</p>
    </details>
  );
}
