import { useEffect, useRef, useState } from "react";
import { ArrowUp } from "lucide-react";

export default function InterfaceEffects({
  viewKey,
  contentKey,
  title,
}: {
  viewKey: string;
  contentKey: string;
  title: string;
}) {
  const [reduced, setReduced] = useState(
    () => window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  );
  const [showTop, setShowTop] = useState(false);
  const revealed = useRef(new WeakSet<Element>());
  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const change = () => {
      setReduced(preference.matches);
      if (preference.matches)
        document
          .getAnimations()
          .filter((animation) => animation.id === "academy-motion")
          .forEach((animation) => animation.cancel());
    };
    preference.addEventListener("change", change);
    return () => preference.removeEventListener("change", change);
  }, []);
  useEffect(() => {
    document.title = `${title} · Practical AI`;
  }, [title, viewKey]);
  useEffect(() => {
    if (reduced) return;
    const target = document.querySelector<HTMLElement>(
      ".workspace-body,.course-overview,.preview-lesson",
    );
    const animation = target?.animate?.(
      [
        { opacity: 0.6, transform: "translateY(8px)" },
        { opacity: 1, transform: "translateY(0)" },
      ],
      { duration: 240, easing: "cubic-bezier(.2,.8,.2,1)" },
    );
    if (animation) animation.id = "academy-motion";
    return () => animation?.cancel();
  }, [viewKey, reduced]);
  useEffect(() => {
    if (reduced || !("IntersectionObserver" in window)) return;
    let order = 0;
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          observer.unobserve(entry.target);
          if (revealed.current.has(entry.target)) continue;
          revealed.current.add(entry.target);
          const animation = (entry.target as HTMLElement).animate?.(
            [
              { opacity: 0.45, transform: "translateY(15px)" },
              { opacity: 1, transform: "translateY(0)" },
            ],
            {
              duration: 420,
              delay: Math.min((order++ % 4) * 35, 105),
              easing: "cubic-bezier(.2,.8,.2,1)",
            },
          );
          if (animation) animation.id = "academy-motion";
        }
      },
      { threshold: 0.08 },
    );
    document
      .querySelectorAll(
        ".hero-copy,.hero-studio,.section-heading,.program-card,.lab-card,.step,.dashboard-course,.surface-card",
      )
      .forEach((element) => {
        if (!revealed.current.has(element)) observer.observe(element);
      });
    return () => observer.disconnect();
  }, [viewKey, contentKey, reduced]);
  useEffect(() => {
    let frame = 0;
    const update = () => {
      if (frame) return;
      frame = requestAnimationFrame(() => {
        setShowTop(window.scrollY > 650);
        frame = 0;
      });
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    return () => {
      window.removeEventListener("scroll", update);
      cancelAnimationFrame(frame);
    };
  }, []);
  return (
    <>
      <a
        className="skip-link"
        href="#main-content"
        onClick={(event) => {
          event.preventDefault();
          const main = document.querySelector<HTMLElement>("main");
          main?.focus({ preventScroll: true });
          main?.scrollIntoView({
            behavior: reduced ? "instant" : "smooth",
            block: "start",
          });
        }}
      >
        Skip to main content
      </a>
      {showTop && (
        <button
          className="back-to-top"
          aria-label="Back to top"
          onClick={() => {
            window.scrollTo({
              top: 0,
              behavior: reduced ? "instant" : "smooth",
            });
            const heading = document.querySelector<HTMLElement>("main h1");
            if (heading) {
              heading.tabIndex = -1;
              heading.focus({ preventScroll: true });
            }
          }}
        >
          <ArrowUp size={19} />
          <span>Back to top</span>
        </button>
      )}
    </>
  );
}
