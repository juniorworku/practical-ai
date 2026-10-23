import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import { readLocal, writeLocal, removeLocal, storageKey } from "./storage";
export default function useNotes(lesson: number, initial: string) {
  const key = storageKey("notes", lesson);
  const draft = useRef(readLocal<{ text: string; base: string }>(key));
  const [notes, setNotes] = useState(draft.current?.text ?? initial);
  const base = useRef(draft.current?.base ?? initial);
  const [dirty, setDirty] = useState(!!draft.current);
  const [message, setMessage] = useState(
    draft.current ? "Recovered a draft from this browser" : "",
  );
  const [saving, setSaving] = useState(false);
  const [blocked, setBlocked] = useState(false);
  const latest = useRef(notes);
  latest.current = notes;
  async function save() {
    if (saving || !dirty) return;
    const text = latest.current;
    setSaving(true);
    try {
      await api(`lessons/${lesson}/notes/`, {
        method: "PUT",
        body: JSON.stringify({ text, base_text: base.current }),
      });
      base.current = text;
      if (latest.current === text) {
        removeLocal(key);
        setDirty(false);
        setMessage("Notes saved");
      } else writeLocal(key, { text: latest.current, base: text });
      setBlocked(false);
    } catch (error) {
      setMessage((error as Error).message + " Draft retained in this browser.");
      setBlocked(true);
    } finally {
      setSaving(false);
    }
  }
  useEffect(() => {
    if (!dirty || saving || blocked) return;
    const timer = window.setTimeout(() => void save(), 900);
    return () => window.clearTimeout(timer);
  }, [notes, dirty, saving, blocked]);
  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => {
      if (dirty && !readLocal(key)) {
        event.preventDefault();
        event.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty, key]);
  function edit(value: string) {
    latest.current = value;
    setNotes(value);
    setDirty(true);
    setBlocked(false);
    setMessage(
      writeLocal(key, { text: value, base: base.current })
        ? "Draft saved on this browser · syncing…"
        : "Browser storage unavailable · keep this page open until saved",
    );
  }
  async function loadAccount() {
    try {
      const data = await api<{ notes?: string }>(`lessons/${lesson}/`);
      writeLocal(key + ":recovery", {
        text: latest.current,
        base: base.current,
      });
      const text = data.notes || "";
      latest.current = text;
      base.current = text;
      setNotes(text);
      setDirty(false);
      setBlocked(false);
      removeLocal(key);
      setMessage(
        "Account notes loaded. The previous browser draft remains available for export.",
      );
    } catch (error) {
      setMessage((error as Error).message);
    }
  }
  function exportDraft() {
    const recovered = readLocal<{ text: string }>(key + ":recovery");
    const url = URL.createObjectURL(
      new Blob(
        [blocked ? latest.current : (recovered?.text ?? latest.current)],
        { type: "text/plain" },
      ),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = "notes-recovery.txt";
    link.click();
    URL.revokeObjectURL(url);
  }
  return {
    notes,
    edit,
    save,
    saving,
    message,
    blocked,
    loadAccount,
    exportDraft,
  };
}
