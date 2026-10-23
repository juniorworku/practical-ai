import { useEffect, useRef, useState } from "react";
import { api } from "./api";
export default function PasswordRecovery({
  uid,
  token,
  onClose,
  onLogin,
}: {
  uid?: string;
  token?: string;
  onClose: () => void;
  onLogin: () => void;
}) {
  const dialog = useRef<HTMLElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const key = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
      if (event.key === "Tab") {
        const items = [
          ...(dialog.current?.querySelectorAll<HTMLElement>(
            "button:not(:disabled),input",
          ) || []),
        ];
        const first = items[0],
          last = items[items.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }
    };
    window.addEventListener("keydown", key);
    return () => {
      window.removeEventListener("keydown", key);
      previous?.focus();
    };
  }, [onClose]);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  return (
    <div className="modal-backdrop">
      <section
        ref={dialog}
        className="auth-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="recovery-title"
      >
        <button
          className="close-modal icon-button"
          onClick={onClose}
          aria-label="Close recovery"
        >
          ×
        </button>
        <h2 id="recovery-title">
          {uid ? "Choose a new password" : "Recover your account"}
        </h2>
        {!done && (
          <form
            onSubmit={async (event) => {
              event.preventDefault();
              const data = Object.fromEntries(
                new FormData(event.currentTarget),
              );
              setBusy(true);
              try {
                const result = await api<{ detail: string }>(
                  uid ? "auth/password-reset/confirm/" : "auth/password-reset/",
                  {
                    method: "POST",
                    body: JSON.stringify({ ...data, uid, token }),
                  },
                  false,
                );
                setStatus(result.detail);
                setDone(true);
              } catch (error) {
                setStatus((error as Error).message);
              } finally {
                setBusy(false);
              }
            }}
          >
            {uid ? (
              <label>
                New password
                <input
                  autoFocus
                  type="password"
                  required
                  minLength={8}
                  name="password"
                  autoComplete="new-password"
                />
              </label>
            ) : (
              <label>
                Account email
                <input
                  autoFocus
                  type="email"
                  required
                  name="email"
                  autoComplete="email"
                />
              </label>
            )}
            <button className="button" disabled={busy}>
              {busy
                ? "Working…"
                : uid
                  ? "Set new password"
                  : "Send recovery email"}
            </button>
          </form>
        )}
        <p role="status">{status}</p>
        <button className="text-button" onClick={onLogin}>
          Return to login
        </button>
      </section>
    </div>
  );
}
