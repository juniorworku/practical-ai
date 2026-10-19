export type Lesson = { id: number; title: string; module: string; minutes: number; content: string; task: string; source_url?: string; source_id?: string; notes?: string; resources?: Record<string, unknown> }
export type Program = { id: number; slug: string; title: string; category: string; description: string; audience: string; outcome: string; duration: string; level: string; lessons: Lesson[] }
export type Profile = { username: string; enrolled: number[]; completed: number[] }
export type Project = { id: number; title: string; problem: string; blueprint: { mode: string; steps: string[]; deliverables: string[] } }
