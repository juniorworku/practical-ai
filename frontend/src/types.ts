export type Lesson = {
  lab?: Lab | null;
  program_slug?: string;
  id: number;
  title: string;
  module: string;
  minutes: number;
  content: string;
  task: string;
  source_url?: string;
  source_id?: string;
  notes?: string;
  learning_summary?: {
    chapters: number;
    concepts: number;
    quiz: number;
    flashcards: number;
    topics: string[];
  };
  resources?: Record<string, unknown>;
};
export type Program = {
  id: number;
  slug: string;
  title: string;
  category: string;
  description: string;
  audience: string;
  outcome: string;
  duration: string;
  level: string;
  lessons: Lesson[];
  pedagogy?: ProgramPedagogy;
  progression?: {
    entry: string;
    independent: boolean;
    checkpoints: { title: string; source_id: string; requirements: number }[];
  } | null;
};
export type Profile = {
  username: string;
  display_name?: string;
  is_staff: boolean;
  enrolled: number[];
  completed: number[];
  positions: Record<number, { lesson: number; chapter: string; updated_at?:string }>;
  progress: {
    practised: number[];
    quiz_passed: number[];
    lab_passed: number[];
    reviewed: number[];
  };
};
export type Project = {
  id: number;
  title: string;
  problem: string;
  blueprint: { mode: string; steps: string[]; deliverables: string[] };
};
export type Learning = {
  revision: string;
  chapters?: { id: string; title: string; body: string; kind: string }[];
  attribution?: { credit: string; revision: string; notice: string };
  concepts: { term: string; definition: string }[];
  questions: { id: string; prompt: string; guidance?: string }[];
  quiz: {
    id: string;
    prompt: string;
    options: { id: string; text: string }[];
  }[];
  flashcards: { id: string; front: string; back: string }[];
  exercise: {
    steps: string[];
    hint: string;
    material?: string;
    hints?: string[];
    solution?: string;
  };
  task: { title: string; deliverable: string; criteria: string[] };
};
export type QuizResult = {
  id: number;
  score: number;
  total: number;
  answers: Record<string, string>;
  feedback: {
    id: string;
    correct: boolean;
    selected: string;
    correct_option: string;
    explanation: string;
  }[];
};
export type Practice = {
  revision: string;
  version: number;
  reflection_answers: Record<string, string>;
  known_cards: string[];
  task_evidence: string;
  checked_criteria: number[];
  task_status: "draft" | "submitted";
  last_quiz: QuizResult | null;
  best_score: number;
  attempt_count: number;
};

export type ModulePedagogy = {
  version: string;
  module: string;
  family: string;
  scenario: string;
  software_first: string;
  production_over_playground: string;
  pillars: { name: string; application: string }[];
  operations: string;
  evaluation_note: string;
  deliverable: string;
  release_gates: string[];
};
export type ProgramPedagogy = {
  version: string;
  software_first: string;
  production_over_playground: string;
  evaluation_note: string;
  pillars: string[];
  modules: ModulePedagogy[];
};
export type Lab = {
  title: string;
  teaching: string;
  starter: string;
  solution: string;
  revision: string;
  checks: { name: string; expression: string; feedback: string }[];
};
export type LabCheck = { name: string; passed: boolean; detail: string };
export type Submission = {
  id: number;
  artifact_url: string;
  commit: string;
  evidence: string;
  measurements: Record<string, string>;
  review_status: string;
  review_feedback: string;
  reviewer: string | null;
  reviewed_at: string | null;
  created_at: string;
  revision: string;
  student?: string;
  lesson?: string;
};
export type ReviewQueue = {
  due_cards: {
    lesson: number;
    program: string;
    id: string;
    front: string;
    back: string;
  }[];
  missed_questions: {
    lesson: number;
    program: string;
    title: string;
    question: string;
  }[];
};
