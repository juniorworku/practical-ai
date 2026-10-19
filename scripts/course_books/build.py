"""Integrate reviewed source teaching into native, independent course books.
Never executes source documents. Keeps pinned provenance and the MIT notice.
"""
import ast,hashlib,json,re
from pathlib import Path
from .plan import PLANS
from .business import CHAPTERS
from .cases import CASES
ROOT=Path(__file__).resolve().parents[2]
SOURCE=json.loads((ROOT/'backend/academy/content/imported_curriculum.json').read_text())
LICENSE=(ROOT/'backend/academy/content/LICENSE.source').read_text()
REVISION=json.loads((ROOT/'backend/academy/content/provenance.json').read_text())['revision']
SKIP={'Further Reading','Ship It','Use It','The Skill','How to read the code','Going further','What You Keep'}
# These source sections make time-sensitive or broad vendor claims that are not
# needed to teach the algorithms. The course uses local examples instead.
SKIP_SUB=['2026','provider comparison','why rag beats fine-tuning','real numbers','numbers you should remember','common embedding models','production patterns','implementations in','tooling','best practice','survey','taxonomy','masft','microsoft taxonomy','role prompting','temperature and sampling','the counterintuitive result']

def clean(text):
    text=re.sub(r'!\[[^\]]*\]\([^)]*\)','',text)
    text=re.sub(r'\[([^\]]+)\]\([^)]*\)',r'\1',text)
    text=re.sub(r'https?://(?:www\.)?(?:github\.com|raw\.githubusercontent\.com)/[^\s)>]+','the pinned teaching source',text)
    text=re.sub(r'```figure\n.*?```','',text,flags=re.S)
    # The reader presents diagrams as a compact text flow rather than broken
    # source-only asset IDs or unrendered Mermaid programs.
    def flow(match):
        lines=[]
        for line in match.group(1).splitlines():
            labels=re.findall(r'\["([^"]+)"\]|\[([^\]]+)\]|\{"([^"]+)"\}',line)
            labels=[next(x for x in label if x).replace('\\n',' / ') for label in labels]
            if labels:lines.append(' → '.join(labels))
        return '\n**System flow**\n\n'+('\n'.join('- '+line for line in lines) if lines else 'Input → validated processing → reviewable output')+'\n'
    text=re.sub(r'```mermaid\n(.*?)```',flow,text,flags=re.S)
    # The course book supplies its own sequence; upstream phase navigation is
    # not a prerequisite and cannot send the learner to another curriculum.
    text=re.sub(r'^.*(?:see|See|Prerequisites:|Related:).*Phase \d.*\n?','',text,flags=re.M)
    text=re.sub(r'(?i)Phase \d+\s*(?:[·:]|lesson)?\s*\d*', 'the related topic',text)
    text=re.sub(r'\n{3,}','\n\n',text)
    return text.strip()

def sections(text):
    """Split only headings outside fenced examples; retain executable examples."""
    result=[];heading=None;lines=[];fenced=False
    for line in text.splitlines():
        if line.startswith('```'):fenced=not fenced
        if not fenced and line.startswith('## '):
            if heading is not None:result.append((heading,'\n'.join(lines).strip()))
            heading=line[3:];lines=[]
        elif heading is not None:lines.append(line)
    if heading is not None:result.append((heading,'\n'.join(lines).strip()))
    return result

def editorial(text):
    # The pinned source is a teaching reference, not current vendor specs or a
    # benchmark we ran. Remove those claims while retaining the algorithms.
    blocks=[]
    for block in text.split('\n\n'):
        if not block.lstrip().startswith('```') and any(name in block for name in ['Claude Opus 4.7 has','Gemini 3 Pro has','Llama 4 claims','Most production RAG systems use','Common embedding models (2026','2026 lineup']):continue
        if block.lstrip().startswith('|') and re.search(r'text-embedding-3|Gemini Embedding|voyage-4|Cohere embed-v4|Best for|Provider.*Notes',block):continue
        block=block.replace('This works 90% of the time. The other 10%','Prompt-only formatting does not guarantee a schema match. On some requests')
        block=block.replace('This is not a model problem. It is an instruction problem.','The request leaves important objectives and constraints unspecified. Improve the specification and evaluate the result before selecting a remedy.')
        if block.startswith('Fine-tuning is one solution. Take the LLM, train it on your internal docs'):
            block='Fine-tuning changes model behavior or learned patterns. Retrieval supplies selected evidence at request time. Choose between them using the task, source freshness, attribution needs and an evaluation; neither is a universal replacement for the other.'
        block=block.replace('For factual knowledge retrieval, RAG wins every time.','For changing factual sources, evaluate retrieval as a baseline and test whether it supports the required answer quality.')
        blocks.append(block)
    return '\n\n'.join(blocks)

def reviewed_body(source):
    result=[]
    for heading,body in sections(source['content']):
        if heading in SKIP or heading in ['Exercises','Key Terms','Learning Objectives']:continue
        if heading=='Build It' and not re.search(r'```(?:python|json|text|markdown|csv)',body):continue
        # Omit dated sub-sections; preserve the rest of the conceptual explanation.
        chunks=re.split(r'(?=^### )',body,flags=re.M)
        chunks=[chunk for chunk in chunks if not (chunk.startswith('### ') and any(s in chunk.splitlines()[0].lower() for s in SKIP_SUB))]
        body=clean(editorial('\n'.join(chunks)))
        if body:result.append('## '+heading+'\n\n'+body)
    return '\n\n'.join(result)

def terms(source):
    blocks=dict(sections(source['content']));rows=[]
    for line in blocks.get('Key Terms','').splitlines():
        if not line.startswith('|'):continue
        cells=[c.strip().strip('`*') for c in line.strip('|').split('|')]
        if len(cells)>=3 and cells[0].lower() not in ['term','concept'] and not set(cells[0])<=set('-: '):
            rows.append({'term':cells[0],'definition':clean(cells[-1])})
    return rows

def function_source(path,name):
    text=path.read_text();tree=ast.parse(text)
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    return '\n'.join(text.splitlines()[node.lineno-1:node.end_lineno])

LABS={
 'retrieve':('Lexical retrieval', '''query = "return unopened item"
passages = [
    {"id": "returns", "text": "An unopened item can be returned within 30 days."},
    {"id": "shipping", "text": "Shipping takes five working days."},
]
assert [p["id"] for p in retrieve(query, passages, 1)] == ["returns"]
assert retrieve("astronomy", passages) == []
''','A matching word does not establish that a policy applies. First prove ranking behavior, then review whether the returned passage actually supports the answer.'),
 'validate_record':('Purchase-record validation', '''valid = {"quantity": 2, "unit_price": "12.50", "total": "25.00", "currency": "USD"}
assert validate_record(valid) == []
assert "total:mismatch" in validate_record(dict(valid, total="24.00"))
assert "quantity:invalid" in validate_record(dict(valid, quantity=True))
''','A schema-valid number can still be wrong. Test arithmetic, missing fields, booleans, negative values and non-finite numbers. Preserve missing values instead of inventing a plausible total.'),
 'validate_citations':('Citation identity checks', '''assert validate_citations("Draft answer", ["policy-1"], ["policy-1"])
assert not validate_citations("Draft answer", ["invented"], ["policy-1"])
assert not validate_citations("Draft answer", ["policy-1", "policy-1"], ["policy-1"])
''','This check establishes reference existence and uniqueness. It does not establish factual entailment. Add a human check that the cited passage supports the exact claim.'),
 'run_agent':('Bounded agent execution', '''assert run_agent(lambda trace: "retrieve", max_steps=2)["status"] == "step_limit"
assert run_agent(lambda trace: "answer", max_steps=2)["status"] == "answer"
assert run_agent(lambda trace: "delete_everything", max_steps=2)["status"] == "failed"
''','A fake decision function isolates control-flow correctness from model quality. Test success, abstention, repeated retrieval, an unknown action and an exception before adding a model adapter.'),
 'routing_metrics':('Routing evaluation', '''result = routing_metrics(["billing", "billing", "technical"], ["billing", "technical", "technical"])
assert result["count"] == 3
assert result["correct"] == 2
assert result["confusion"]["billing"]["technical"] == 1
''','Aggregate accuracy hides which route is harmed. Read rows as expected classes and columns as predictions, then examine the cost and review burden of each confusion.'),
 'net_minutes':('Workflow benefit calculation', '''assert net_minutes(40, 20, 4, 10, 0.2, 15) == 120
assert net_minutes(40, 20, 4, 14, 0.3, 15) == -100
''','The function includes assisted review and exception work but excludes monthly maintenance; subtract maintenance separately. A negative result is evidence to investigate or stop, not a number to hide.'),
}

def lab_for(slug,index):
    if slug=='ai-agent-bootcamp':return 'retrieve' if index<9 else 'validate_citations' if index==9 else 'run_agent' if index<16 else 'routing_metrics' if index in [16,23] else 'run_agent'
    if slug=='ai-workshops':return ['validate_record','run_agent','validate_citations','routing_metrics','validate_citations','run_agent'][(index-1)//3]
    return 'net_minutes' if index in [1,3,4,6,11,17] else 'validate_record' if index==7 else 'validate_citations' if index in [10,16] else 'run_agent'

def enrich(programs):
    manifest=[]
    for course in programs:
        plan=PLANS[course['slug']]
        assert len(plan)==len(course['lessons'])
        for index,(lesson,keys) in enumerate(zip(course['lessons'],plan),1):
            learning=lesson['resources']['learning'];chapters=[];provenance=[]
            # Business teaching comes first: the technical reference serves the
            # engagement, rather than turning freelancing into an agent course.
            if course['slug']=='freelancing-masterclass':
                title,body=CHAPTERS[index-1];chapters.append({'id':'business','title':title,'body':body.strip(),'kind':'Client delivery'})
            extras=[];extra_quiz=[];source_exercises=[]
            if course['slug']=='freelancing-masterclass':
                for block in re.split(r'(?=^### )',CHAPTERS[index-1][1],flags=re.M):
                    if block.startswith('### '):
                        heading,paragraph=block.split('\n',1)
                        if 'exercise' not in heading.lower() and 'practice' not in heading.lower():
                            definition=paragraph.strip().split('\n\n')[0]
                            extras.append({'term':heading[4:],'definition':' '.join(re.split(r'(?<=[.!?])\s+',definition)[:2])})
            for seq,(phase,order) in enumerate(keys,1):
                source=next(p for p in SOURCE if p['slug']==f'library-phase-{phase:02}')['lessons'][order]
                body=reviewed_body(source)
                chapters.append({'id':f'teaching-{seq}','title':source['title'],'body':body,'kind':'Concepts & implementation'})
                extras.extend(terms(source))
                exercises=dict(sections(source['content'])).get('Exercises','')
                if exercises:source_exercises.append('### '+source['title']+'\n\n'+clean(exercises))
                for qindex,q in enumerate(source['resources'].get('quiz',[])):
                    if not isinstance(q,dict) or not isinstance(q.get('correct'),int) or not isinstance(q.get('options'),list):continue
                    if q.get('stage')=='pre':continue
                    if re.search(r'2026|Phase \d|arxiv|version|which (?:provider|framework|sdk|library)',q.get('question',''),re.I):continue
                    extra_quiz.append({'id':f'chapter-{seq}-q{qindex}','prompt':clean(q['question']),'options':[{'id':chr(97+i),'text':clean(str(o))} for i,o in enumerate(q['options'])],'correct':chr(97+q['correct']),'explanation':clean(q.get('explanation','Review the explanation in this concept chapter.'))})
                example=ROOT/'backend/academy/content/embedded_examples'/f'{phase:02}-{order:02}.py.txt'
                if example.exists():
                    chapters.append({'id':f'code-{seq}','title':source['title']+' · implementation walkthrough','body':'Read the control flow before running or changing it. This pinned teaching implementation illustrates the chapter; source-specific dependencies and fixtures are named in its code. The short exercise in the Exercise tab is a separate standard-library practice.\n\n```python\n'+example.read_text().strip()+'\n```','kind':'Code study'})
                provenance.append({'source_id':source['source_id'],'title':source['title'],'revision':REVISION})
            if course['slug']=='ai-agent-bootcamp' and index==12:
                chapters.append({'id':'approval-runtime','title':'Approval records, atomic claims and uncertain outcomes','kind':'Implementation design','body':"""## Separate proposal, authority and execution
A model proposes an action. An authenticated reviewer approves an exact payload revision. A dispatcher verifies permission again and executes the approved action. These are three different events. Store action ID, tenant scope, payload revision, payload digest, approving actor, approval time, expiry and execution status. An action ID alone is not permission.

## Bind the decision to what was reviewed
Canonicalize the fields that determine the effect: recipient, destination account, amount where relevant, and content revision. Save their digest with the approval. If a field changes, return the action to review. Rechecking the digest prevents an approval for one recipient being reused for another. Also check that the approving actor still has authority when execution begins; a revoked role must not remain effective because an old approval exists.

## Claim work atomically
Two workers can both read “approved” before either updates the row. A read followed by an unrelated write is not a lock. Use an atomic conditional update or an appropriate database lock and a uniqueness constraint on the scoped idempotency key. Only the worker that successfully claims the action should proceed. Define what happens when a worker crashes after claiming it so the action does not remain stuck forever.

```text
proposed -> approved(revision 2) -> claimed(key K) -> committed
                       |                 |
                 payload changes    response lost
                       v                 v
                 needs review       reconcile K
```

## A timeout is an uncertain outcome
Suppose the destination accepted an email but the response was lost. A timeout means you do not know the outcome; it does not mean nothing happened. Preserve the same idempotency key and inspect the destination or effect ledger before retrying. If the destination supports idempotency, send the same key on a retry. If it does not, document the limits of duplicate prevention and choose an appropriate review or reconciliation path. Do not claim exactly-once external effects merely because a database row is unique.

## Local rollback does not undo the outside world
A database rollback can remove an uncommitted local change. It cannot unsend an accepted email. Record proposed, claimed, uncertain, committed and failed outcomes separately, and design recovery for each. Some effects can be compensated; compensation is a new action with its own authorization and failure modes, not time travel. Start the experiment with a fake destination that stores keys and effects so you can observe duplicates without sending anything.

## Failure experiment
Use a fake destination that records a key, then raises a timeout before returning. Restart the worker and present the same action again. Inspect the recorded key before allowing a new effect. Repeat with two workers, an edited recipient, and a revoked reviewer role. Your evidence should show one effect for a committed key, a visible uncertain state when confirmation is missing, and no execution of an unapproved revision.
"""})
            # The academy case connects the source concepts to this path's own
            # evolving project and includes its original worked example/rubric.
            original=lesson['content']
            chapters.append({'id':'case-study','title':'Apply it: '+lesson['title'],'body':clean(original.split('\n',1)[1]),'kind':'Worked case & project'})
            seen={c['term'].lower() for c in learning['concepts']}
            for term in extras:
                if term['term'].lower() not in seen:
                    learning['concepts'].append(term);seen.add(term['term'].lower())
                    learning['flashcards'].append({'id':f'concept-{len(learning["flashcards"])+1}','front':term['term'],'back':term['definition']})
            prompts={q['prompt'] for q in learning['quiz']}
            for q in extra_quiz:
                if q['prompt'] not in prompts:learning['quiz'].append(q);prompts.add(q['prompt'])
            if course['slug']=='ai-agent-bootcamp' and index==12:
                approval_questions=[
                    ('The recipient changes after approval. What should execution do?','Require a new approval for the changed revision.','Use the old approval because the action ID is unchanged.','Ask the model whether the edit matters.','Approval binds the reviewed payload and revision; an edited recipient changes the consequential action.'),
                    ('A send request times out after the destination accepted it. What is the safest next step?','Check the persisted idempotency record and destination outcome before retrying.','Retry with a new key immediately.','Mark the job failed and forget the previous attempt.','A lost response does not prove the effect failed. Reconcile the existing key before replaying a write.'),
                    ('Which actor may approve a proposed consequential action?','An authenticated actor authorized for that action and scope.','The model that proposed it.','Any account that knows the action ID.','Approval is an application permission, verified independently of a model response or a guessed identifier.'),
                    ('Two workers claim the same approved action. Which control is needed?','An atomic claim or unique idempotency constraint around the effect.','A longer instruction telling workers to avoid duplicates.','A random pause before each write.','Concurrency needs a storage or destination guarantee; timing and prose do not prevent both workers from acting.'),
                    ('A database transaction rolls back after an email was sent. What follows?','The external email still exists; reconcile and design recovery explicitly.','The recipient automatically loses the email.','The model can declare the send undone.','A local database rollback cannot reverse a completed external side effect. Keep effect status, reconciliation and any compensation explicit.'),
                ]
                for number,(prompt,right,wrong1,wrong2,explanation) in enumerate(approval_questions,1):
                    choices=[right,wrong1,wrong2];shift=number%3;choices=choices[shift:]+choices[:shift]
                    learning['quiz'].append({'id':f'approval-{number}','prompt':prompt,'options':[{'id':chr(97+i),'text':text} for i,text in enumerate(choices)],'correct':chr(97+choices.index(right)),'explanation':explanation})
            learning['questions'].extend([
                {'id':'diagnosis','prompt':f'For “{lesson["title"]}”, describe a failure that could pass the happy-path test. Which input, observation and check would expose it?'},
                {'id':'transfer','prompt':'Change one assumption in the worked case: input quality, volume, permission or reviewer capacity. Explain which part of the design must change and which evidence you would collect before accepting it.'},
            ])
            title,fixture,expected,why,variation=CASES[course['slug']][index-1]
            material='## '+title+'\n\n### 1. Inspect the input and predict the outcome\n\nWrite down your decision before reading the walkthrough. Name the boundary, the relevant evidence, and the output that should be blocked or permitted.\n\n```json\n'+json.dumps(fixture,indent=2,ensure_ascii=False)+'\n```\n\n### 2. Work through the decision\n\n'+why+'\n\nThe expected observation for this example is:\n\n```json\n'+json.dumps(expected,indent=2,ensure_ascii=False)+'\n```\n\n### 3. Change an assumption\n\n'+variation+'\n\n### 4. Record your own experiment\n\nUse the lesson-specific steps above to build or role-play the workflow. Record input revision, prediction, actual observation, discrepancy, decision and remaining uncertainty. In coding lessons, implement and run it in your own scratch environment. In client-delivery lessons, complete the named analysis or artifact. The academy saves written evidence; it does not run code or pretend to verify external work.\n'
            matched={'ai-agent-bootcamp':{8:'retrieve',9:'validate_citations',11:'run_agent',16:'run_agent'},'ai-workshops':{2:'validate_record',3:'validate_record',8:'validate_citations',11:'routing_metrics'},'freelancing-masterclass':{3:'net_minutes',6:'net_minutes'}}
            name=matched[course['slug']].get(index)
            if name:
                labtitle,checks,comment=LABS[name]
                starter=function_source(ROOT/'backend/academy/content/program_labs/exercises.py',name)
                reference=function_source(ROOT/'backend/academy/content/program_labs/reference.py',name)
                material+='\n## Coding experiment: '+labtitle+'\n\n'+comment+'\n\n### Behavioral checks\n\n```python\n'+checks+'```\n\n### Starter to implement\n\n```python\n'+starter+'\n```\n\n### Reference implementation to explain and extend\n\n```python\nimport re\nfrom decimal import Decimal, InvalidOperation\n\n'+reference+'\n```\n'
            if source_exercises:material+='\n## Further experiments on these concepts\n\n'+('\n\n'.join(source_exercises))
            learning['exercise']['material']=material
            learning['chapters']=chapters
            learning['attribution']={'notice':LICENSE,'credit':'Concept teaching adapted from AI Engineering from Scratch by Rohit Ghumare. The academy adds the program sequence, client-delivery teaching, contextual cases and exercise guidance.','revision':REVISION}
            learning['revision']=hashlib.sha256(json.dumps({k:v for k,v in learning.items() if k!='revision'},sort_keys=True).encode()).hexdigest()
            lesson['content']='# '+lesson['title']+'\n\n'+'\n\n'.join('## '+c['title']+'\n\n'+c['body'] for c in chapters)
            lesson['content_hash']=hashlib.sha256(lesson['content'].encode()).hexdigest()
            lesson['source_url']=''
            lesson['resources']['revision']='academy-course-books-v4'
            lesson['resources']['provenance']=provenance
            lesson['resources']['references']=[]
            lesson['minutes']=max(lesson['minutes'],round(len(lesson['content'].split())/160)+90)
            manifest.append({'program':course['slug'],'lesson':index,'title':lesson['title'],'chapters':len(chapters),'words':len(lesson['content'].split()),'concepts':len(learning['concepts']),'quiz':len(learning['quiz']),'cards':len(learning['flashcards']),'source_topics':provenance})
    (ROOT/'docs/course-book-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
