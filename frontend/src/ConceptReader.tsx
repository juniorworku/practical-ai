import {useState} from 'react'
import {ArrowLeft,ArrowRight,BookOpen,Check} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type {Learning} from './types'

export function TeachingMarkdown({children}:{children:string}) {
 return <div className="markdown-reader"><ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml components={{
  img:()=>null,
  a:({children})=><span>{children}</span>,
 }}>{children}</ReactMarkdown></div>
}

export default function ConceptReader({learning,onPractice,initialChapterId}:{learning:Learning;onPractice:()=>void;initialChapterId?:string}) {
 const chapters=learning.chapters||[]
 const [chapter,setChapter]=useState(()=>Math.max(0,chapters.findIndex(c=>c.id===initialChapterId)))
 const active=chapters[chapter]
 function select(index:number){setChapter(index);document.getElementById('chapter-reading')?.scrollIntoView({block:'start',behavior:'smooth'})}
 if(!active)return null
 return <div className="course-book">
  <div className="book-intro"><span className="eyebrow">THE LESSON BOOK</span><p>Read the concept chapters and implementation, then work through the case. The Exercise tab contains the input, walkthrough, checks and failure experiments.</p></div>
  <details className="book-contents"><summary><BookOpen size={16}/><span>Contents · {chapters.length} chapters</span><strong>{active.title}</strong></summary><nav className="chapter-index" aria-label="Lesson chapters">{chapters.map((item,index)=><button key={item.id} aria-current={chapter===index?'step':undefined} onClick={()=>select(index)}><span>{String(index+1).padStart(2,'0')}</span><div><small>{item.kind}</small><strong>{item.title}</strong></div>{chapter===index?<BookOpen size={15}/>:<ArrowRight size={15}/>}</button>)}</nav></details>
  <article id="chapter-reading" className="chapter-reading" aria-label="Chapter reading"><div className="chapter-caption"><span className="eyebrow">CHAPTER {chapter+1} OF {chapters.length} · {active.kind}</span><span>~{Math.max(1,Math.ceil(active.body.split(/\s+/).length/180))} min reading</span></div><h2>{active.title}</h2><TeachingMarkdown>{active.body}</TeachingMarkdown></article>
  <div className="chapter-actions"><button className="text-button" disabled={chapter===0} onClick={()=>select(chapter-1)}><ArrowLeft size={16}/>Previous chapter</button>{chapter<chapters.length-1?<button className="button" onClick={()=>select(chapter+1)}>Next chapter<ArrowRight size={16}/></button>:<button className="button" onClick={onPractice}>Begin the exercise<ArrowRight size={16}/></button>}</div>
  <details className="lesson-glossary"><summary>{learning.concepts.length} concepts explained in this lesson</summary><dl>{learning.concepts.map(c=><div key={c.term}><dt><Check size={13}/>{c.term}</dt><dd>{c.definition}</dd></div>)}</dl></details>
  {learning.attribution&&<details className="teaching-credit"><summary>Teaching credits & license</summary><p>{learning.attribution.credit}</p><small>Source snapshot {learning.attribution.revision.slice(0,12)}. This lesson is taught here; no external course is required.</small><pre>{learning.attribution.notice}</pre></details>}
 </div>
}
