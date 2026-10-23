import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  ArrowRight,
  BookOpen,
  Check,
  Eye,
  EyeOff,
  Layers3,
  LockKeyhole,
  X,
} from "lucide-react";
export default function AuthDialog({
  register,
  busy,
  error,
  onClose,
  onSwitch,
  onRecovery,
  onSubmit,
}: {
  register: boolean;
  busy: boolean;
  error: string;
  onClose: () => void;
  onSwitch: () => void;
  onRecovery: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  const dialog = useRef<HTMLElement>(null);
  const form = useRef<HTMLFormElement>(null);
  const [visible, setVisible] = useState(false);
  const [caps, setCaps] = useState(false);
  const [localError, setLocalError] = useState("");
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    dialog.current?.querySelector<HTMLInputElement>("input")?.focus();
    const key = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !busy) onClose();
      if (event.key === "Tab") {
        const items = [
          ...(dialog.current?.querySelectorAll<HTMLElement>(
            "button:not(:disabled),input:not(:disabled)",
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
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", key);
    return () => {
      document.body.style.overflow = overflow;
      window.removeEventListener("keydown", key);
      previous?.focus();
    };
  }, [busy, onClose]);
  return (
    <div
      className="modal-backdrop auth-backdrop"
      onClick={(event) => {
        if (event.target === event.currentTarget && !busy) onClose();
      }}
    >
      <section
        ref={dialog}
        className="auth-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-title"
      >
        <aside className="auth-story">
          <span className="brand-mark">
            <Layers3 />
          </span>
          <span className="eyebrow">PRACTICAL AI ACADEMY</span>
          <h2>
            Your next idea
            <br />
            deserves a<br />
            <em>working version.</em>
          </h2>
          <p>
            A learning space for people who want to understand AI by building
            with it.
          </p>
          <ul>
            <li>
              <Check size={16} />
              Independent programs, free to join
            </li>
            <li>
              <Check size={16} />
              Real examples and deliberate practice
            </li>
            <li>
              <Check size={16} />
              Your notes and progress, saved
            </li>
          </ul>
          <div className="auth-story-note">
            <BookOpen size={24} />
            <span>
              Learn the concept.
              <br />
              <strong>Build the evidence.</strong>
            </span>
          </div>
        </aside>
        <div className="auth-form-side">
          <button
            className="close-modal icon-button"
            aria-label="Close"
            disabled={busy}
            onClick={onClose}
          >
            <X size={20} />
          </button>
          <div className="auth-mode" role="group" aria-label="Account access">
            <button
              className={!register ? "selected" : ""}
              onClick={() => {
                if (register) {
                  form.current?.reset();
                  setLocalError("");
                  onSwitch();
                }
              }}
              disabled={busy}
            >
              Sign in
            </button>
            <button
              className={register ? "selected" : ""}
              onClick={() => {
                if (!register) {
                  form.current?.reset();
                  setLocalError("");
                  onSwitch();
                }
              }}
              disabled={busy}
            >
              Create account
            </button>
          </div>
          <span className="eyebrow">
            {register ? "START SOMETHING USEFUL" : "PICK UP WHERE YOU LEFT OFF"}
          </span>
          <h2 id="auth-title">
            {register ? "Make room for possibility." : "Welcome back."}
          </h2>
          <p>
            {register
              ? "Your account is free. Choose your own learning path."
              : "Sign in to your lessons, projects and learning notebook."}
          </p>
          {(error || localError) && (
            <div className="error" role="alert">
              {localError || error}
            </div>
          )}
          <form
            ref={form}
            onSubmit={(event) => {
              setLocalError("");
              if (register) {
                const data = new FormData(event.currentTarget);
                if (data.get("password") !== data.get("confirm_password")) {
                  event.preventDefault();
                  setLocalError(
                    "Your passwords do not match. Please check both fields.",
                  );
                  return;
                }
              }
              onSubmit(event);
            }}
          >
            <fieldset disabled={busy}>
              {register && (
                <label htmlFor="auth-name">
                  What should we call you?
                  <input
                    id="auth-name"
                    name="display_name"
                    maxLength={100}
                    autoComplete="given-name"
                    placeholder="Your first name (optional)"
                  />
                </label>
              )}
              <label htmlFor="auth-username">
                {register ? "Username" : "Username or email"}
                <input
                  id="auth-username"
                  name="username"
                  aria-label="Username"
                  required
                  maxLength={150}
                  autoComplete="username"
                  placeholder={
                    register ? "Choose a username" : "you@example.com"
                  }
                  autoCapitalize="none"
                  spellCheck={false}
                />
              </label>
              {register && (
                <label htmlFor="auth-email">
                  Email address
                  <input
                    id="auth-email"
                    name="email"
                    type="email"
                    required
                    autoComplete="email"
                    placeholder="you@example.com"
                  />
                </label>
              )}
              <label htmlFor="auth-password">Password</label>
              <div className="password-control">
                <input
                  id="auth-password"
                  name="password"
                  required
                  type={visible ? "text" : "password"}
                  minLength={register ? 8 : undefined}
                  autoComplete={register ? "new-password" : "current-password"}
                  onKeyUp={(event) =>
                    setCaps(event.getModifierState("CapsLock"))
                  }
                  placeholder={
                    register ? "At least 8 characters" : "Enter your password"
                  }
                />
                <button
                  type="button"
                  onClick={() => setVisible(!visible)}
                  aria-label={visible ? "Hide password" : "Show password"}
                >
                  {visible ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {caps && <small role="status">Caps Lock is on.</small>}
              {register ? (
                <>
                  <small>
                    Use a unique password. Avoid common words and personal
                    details.
                  </small>
                  <label htmlFor="auth-confirm">
                    Confirm password
                    <input
                      id="auth-confirm"
                      name="confirm_password"
                      type={visible ? "text" : "password"}
                      required
                      minLength={8}
                      autoComplete="new-password"
                    />
                  </label>
                </>
              ) : (
                <div className="auth-options">
                  <label className="checkbox-label">
                    <input name="remember" type="checkbox" />
                    Remember this device
                  </label>
                  <button
                    type="button"
                    className="text-button"
                    onClick={onRecovery}
                  >
                    Forgot password?
                  </button>
                </div>
              )}
              <button
                className="button auth-submit"
                type="submit"
                disabled={busy}
              >
                {busy
                  ? "One moment…"
                  : register
                    ? "Create free account"
                    : "Log in"}
                <ArrowRight size={18} />
              </button>
            </fieldset>
          </form>
          <p className="auth-privacy">
            <LockKeyhole size={13} />
            Your learning work stays private to your account.
          </p>
        </div>
      </section>
    </div>
  );
}
