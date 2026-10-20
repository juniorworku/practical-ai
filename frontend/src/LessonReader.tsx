import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ArrowUpRight, Check, LoaderCircle, Save } from 'lucide-react'
import { api } from './api'
import LearningStudio from './LearningStudio'
import EngineeringContract from './EngineeringContract'
import type { Lesson, Learning, ModulePedagogy } from './types'
export default function LessonReader({lesson, loading, onError, onDownloadKit}: {lesson: Lesson; loading: boolean; onError: (error: string) => void; onDownloadKit: () => Promise<void>}) {
  const [notes, setNotes] = useState('')
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)
  useEffect(() => {setNotes(lesson.notes || ''); setSaved(false)}, [lesson.id, lesson.notes])
  async function save() {
    setSaving(true)
    try {await api(`lessons/${lesson.id}/notes/`, {method:'PUT',body:JSON.stringify({text:notes})}); setSaved(true)} catch(e) {onError((e as Error).message)} finally {setSaving(false)}
  }
  const content = lesson.content?.startsWith('# '+lesson.title+'\n') ? lesson.content.slice(lesson.title.length+3).trimStart() : lesson.content
  if (loading) return <div className="flex items-center gap-3 py-10 text-brand" role="status"><LoaderCircle className="spin" size={18}/> Opening your reading…</div>
  const learning=lesson.resources?.learning as Learning | undefined
  if (learning) return <LearningStudio key={lesson.id} lesson={lesson} learning={learning} content={content} onError={onError}/>
  return <>
    {lesson.resources?.pedagogy ? <EngineeringContract contract={lesson.resources.pedagogy as ModulePedagogy}/> : null}
    {lesson.source_id && <div className="source-note"><span>{lesson.source_id.startsWith('academy-v2:') ? 'Practical academy program' : 'Workshop source'} · {lesson.source_id.split(':').pop()}</span>{lesson.source_url && <a href={lesson.source_url} target="_blank" rel="noreferrer">View source <ArrowUpRight size={12}/></a>}</div>}
    {lesson.source_id?.startsWith('academy-v2:') && <div className="practical-brief"><span className="eyebrow">BUILD · TEST · EXPLAIN</span><p><strong>Your artifact:</strong> <code>{String(lesson.resources?.artifact || '')}</code></p><p><strong>Program capstone:</strong> {String(lesson.resources?.capstone || '')}</p><button className="text-button" onClick={onDownloadKit}>Download offline labs & worksheets <ArrowUpRight size={14}/></button><small>Run exercises in a separate local workspace. No code runs inside this lesson reader.</small></div>}
    <div className="markdown-reader"><ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml components={{img: () => <span className="blocked-image">[Illustration omitted from imported source]</span>, a: ({href, children}) => <a href={href} target="_blank" rel="noreferrer">{children}</a>}}>{content}</ReactMarkdown></div>
    {lesson.resources && ['code','quiz'].map(key => lesson.resources?.[key] ? <details className="source-artifact" key={key}><summary>{key === 'code' ? 'Original source code references' : 'Original source quiz & answer reference'}</summary><pre>{typeof lesson.resources[key] === 'string' ? lesson.resources[key] as string : JSON.stringify(lesson.resources[key],null,2)}</pre></details> : null)}
    <div className="learner-notes"><label htmlFor="notes">Your notes & observations</label><textarea id="notes" rows={4} value={notes} onChange={e => {setNotes(e.target.value);setSaved(false)}} maxLength={10000} placeholder="What did you try? What did you observe? Save before switching lessons."/><div className="flex items-center justify-between gap-3"><small>Private to your account. Save before leaving this lesson.</small><button className="text-button" onClick={save} disabled={saving}>{saved ? <Check size={14}/> : <Save size={14}/>} {saving ? 'Saving…' : saved ? 'Saved' : 'Save notes'}</button></div></div>
  </>
}
