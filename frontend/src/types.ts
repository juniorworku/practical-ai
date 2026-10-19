export type Lesson = { id: number; title: string; module: string; minutes: number; content: string; task: string; source_url?: string; source_id?: string; notes?: string; learning_summary?: {chapters:number;concepts:number;quiz:number;flashcards:number;topics:string[]}; resources?: Record<string, unknown> }
export type Program = { id: number; slug: string; title: string; category: string; description: string; audience: string; outcome: string; duration: string; level: string; lessons: Lesson[] }
export type Profile = { username: string; enrolled: number[]; completed: number[] }
export type Project = { id: number; title: string; problem: string; blueprint: { mode: string; steps: string[]; deliverables: string[] } }
export type Learning = {
 revision: string
 chapters?: {id:string;title:string;body:string;kind:string}[]
 attribution?: {credit:string;revision:string;notice:string}
 concepts: {term:string;definition:string}[]
 questions: {id:string;prompt:string}[]
 quiz: {id:string;prompt:string;options:{id:string;text:string}[]}[]
 flashcards: {id:string;front:string;back:string}[]
 exercise: {steps:string[];hint:string;material?:string}
 task: {title:string;deliverable:string;criteria:string[]}
}
export type QuizResult = {id:number;score:number;total:number;answers:Record<string,string>;feedback:{id:string;correct:boolean;selected:string;correct_option:string;explanation:string}[]}
export type Practice = {revision:string;version:number;reflection_answers:Record<string,string>;known_cards:string[];task_evidence:string;checked_criteria:number[];task_status:'draft'|'submitted';last_quiz:QuizResult|null;best_score:number;attempt_count:number}
