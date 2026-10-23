import { useEffect, useRef, useState } from "react";
import { BookOpen, Check, ChevronRight, ListTree, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import type { Program, Lesson } from "./types";

type Props = {
  program: Program;
  lesson: Lesson;
  completed: number[];
  query: string;
  onQuery: (query: string) => void;
  onLesson: (id: number) => void;
};
export function CourseModuleNav({
  program,
  lesson,
  onLesson,
}: Pick<Props, "program" | "lesson" | "onLesson">) {
  const modules = [...new Set(program.lessons.map((item) => item.module))];
  const nav = useRef<HTMLElement>(null);
  useEffect(() => {
    const active = nav.current?.querySelector<HTMLElement>("[aria-current]");
    if (nav.current && active)
      nav.current.scrollLeft +=
        active.getBoundingClientRect().left -
        nav.current.getBoundingClientRect().left -
        24;
  }, [lesson.module]);
  return (
    <nav ref={nav} className="course-module-nav" aria-label="Program modules">
      {modules.map((module, index) => (
        <Button
          key={module}
          variant="ghost"
          aria-current={lesson.module === module ? "step" : undefined}
          onClick={() =>
            onLesson(program.lessons.find((item) => item.module === module)!.id)
          }
        >
          <span>{String(index + 1).padStart(2, "0")}</span>
          {module.replace(/^\d+\s*[·.:—-]\s*/, "")}
        </Button>
      ))}
    </nav>
  );
}
export default function CourseNavigation(props: Props) {
  const [open, setOpen] = useState(false);
  const sidebar = useRef<HTMLElement>(null);
  const [openModules, setOpenModules] = useState(() => [
    ...new Set(props.program.lessons.map((item) => item.module)),
  ]);
  useEffect(() => {
    setOpenModules((previous) =>
      previous.includes(props.lesson.module)
        ? previous
        : [...previous, props.lesson.module],
    );
    const frame = requestAnimationFrame(() => {
      const active = sidebar.current?.querySelector<HTMLElement>(".current");
      if (sidebar.current && active) {
        const bounds = sidebar.current.getBoundingClientRect(),
          item = active.getBoundingClientRect();
        if (item.top < bounds.top || item.bottom > bounds.bottom)
          sidebar.current.scrollTop +=
            item.top - bounds.top - bounds.height / 3;
      }
    });
    return () => cancelAnimationFrame(frame);
  }, [props.lesson.id, props.lesson.module]);
  const [mobile, setMobile] = useState(
    () => matchMedia("(max-width:1000px)").matches,
  );
  useEffect(() => {
    const media = matchMedia("(max-width:1000px)");
    const change = () => {
      setMobile(media.matches);
      if (!media.matches) setOpen(false);
    };
    media.addEventListener("change", change);
    return () => media.removeEventListener("change", change);
  }, []);
  const modules = [
    ...new Set(props.program.lessons.map((item) => item.module)),
  ];
  const visible = props.program.lessons.filter((item) =>
    (item.title + " " + item.module)
      .toLowerCase()
      .includes(props.query.toLowerCase()),
  );
  const count = props.program.lessons.filter((item) =>
    props.completed.includes(item.id),
  ).length;
  function choose(id: number) {
    props.onLesson(id);
    setOpen(false);
  }
  function contents() {
    return (
      <div className="course-sidebar-content">
        <div className="course-sidebar-heading">
          <BookOpen size={18} />
          <strong>{props.program.title}</strong>
        </div>
        <div className="course-sidebar-progress">
          <span>
            {count} / {props.program.lessons.length} lessons read
          </span>
          <Badge variant="outline">Free</Badge>
        </div>
        <Progress
          value={(count / props.program.lessons.length) * 100}
          aria-label="Program reading progress"
        />
        <label className="course-lesson-search">
          <Search size={16} />
          <Input
            aria-label="Search lessons"
            placeholder="Search this program…"
            value={props.query}
            onChange={(e) => props.onQuery(e.target.value)}
          />
        </label>
        <Accordion
          type="multiple"
          value={openModules}
          onValueChange={setOpenModules}
          className="course-groups"
        >
          {modules
            .filter((module) => visible.some((item) => item.module === module))
            .map((module) => (
              <AccordionItem value={module} key={module}>
                <AccordionTrigger>{module}</AccordionTrigger>
                <AccordionContent>
                  {visible
                    .filter((item) => item.module === module)
                    .map((item) => (
                      <Button
                        key={item.id}
                        variant="ghost"
                        className={item.id === props.lesson.id ? "current" : ""}
                        aria-current={
                          item.id === props.lesson.id ? "page" : undefined
                        }
                        onClick={() => choose(item.id)}
                      >
                        {props.completed.includes(item.id) ? (
                          <Check size={15} />
                        ) : (
                          <ChevronRight size={15} />
                        )}
                        <span>{item.title}</span>
                      </Button>
                    ))}
                </AccordionContent>
              </AccordionItem>
            ))}
        </Accordion>
        {!visible.length && (
          <div className="lesson-search-empty" role="status">
            <p>No lessons match “{props.query}”.</p>
            <Button variant="outline" onClick={() => props.onQuery("")}>
              Clear lesson search
            </Button>
          </div>
        )}
      </div>
    );
  }
  return (
    <>
      <aside
        ref={sidebar}
        className="course-sidebar"
        aria-label="Course lessons"
      >
        {!mobile && contents()}
      </aside>
      <div className="mobile-course-bar">
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="outline">
              <ListTree size={17} />
              Course contents
            </Button>
          </SheetTrigger>
          <SheetContent
            onOpenAutoFocus={(event) => {
              const active = document.querySelector<HTMLElement>(
                ".course-sheet .current",
              );
              if (active) {
                event.preventDefault();
                active.focus();
              }
            }}
            side="left"
            className="course-sheet"
          >
            <SheetHeader>
              <SheetTitle>Your learning path</SheetTitle>
              <SheetDescription>
                Choose a lesson. Your saved work stays with your account.
              </SheetDescription>
            </SheetHeader>
            {open && contents()}
          </SheetContent>
        </Sheet>
        <span>
          {props.program.lessons.findIndex(
            (item) => item.id === props.lesson.id,
          ) + 1}{" "}
          / {props.program.lessons.length}
        </span>
      </div>
    </>
  );
}
