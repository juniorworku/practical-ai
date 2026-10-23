import { Component, type ReactNode } from "react";
import { Layers3, RefreshCw } from "lucide-react";
export default class ErrorBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <main id="main-content" tabIndex={-1} className="recovery-screen wrap">
        <section className="surface-card" role="alert">
          <span className="brand-mark">
            <Layers3 size={26} />
          </span>
          <span className="eyebrow">PRACTICAL AI ACADEMY</span>
          <h1>This page couldn’t be opened.</h1>
          <p>
            The connection may have changed, or the app may have been updated.
            Reload to try again.
          </p>
          <button className="button" onClick={() => window.location.reload()}>
            <RefreshCw size={17} />
            Reload page
          </button>
        </section>
      </main>
    );
  }
}
