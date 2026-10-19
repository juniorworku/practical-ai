from pathlib import Path
import hashlib
ROOT = Path(__file__).resolve().parents[2]
PROGRAMS=[]

def program(slug,title,category,description,audience,outcome,duration,order,prerequisites,capstone):
    value=dict(slug=slug,title=title,category=category,description=description,audience=audience,outcome=outcome,duration=duration,order=order,level=prerequisites,lessons=[])
    value['_capstone']=capstone
    PROGRAMS.append(value)
    return value

def lesson(p,module,title,concept,example,build,failure,checks,artifact,minutes=120,reading=None):
    number=len(p['lessons'])+1
    references=reading or []
    content=f'''# {title}

## The engineering or business decision

{concept}

## Worked example

{example}

## Build it yourself

'''+ '\n'.join(f'{i+1}. {line}' for i,line in enumerate(build))+f'''

## Break it deliberately

{failure}

## Acceptance checks

'''+ '\n'.join('- '+line for line in checks)+f'''

## Deliverable

Save **`{artifact}`** in your separate program workspace. Include your inputs, actual outputs, decisions, and unresolved limitations. Budget about **{minutes} minutes** for reading, implementation and review; this is an estimate, not a timed requirement.

## Explain your judgment

Which acceptance check would change your decision if it failed? Explain what your artifact demonstrates and what it cannot establish. Completion in this academy records your own report; the platform does not execute your work or certify it.
'''
    if references:
        content+='\n## Further reading\n\n'+'\n'.join(f'- [{label}]({url})' for label,url in references)+'\n'
    p['lessons'].append(dict(title=title,module=module,order=number-1,minutes=minutes,content=content,task='\n'.join(build),source_id=f"academy-v2:{p['slug']}:{number:02}",source_url=references[0][1] if references else '',content_hash=hashlib.sha256(content.encode()).hexdigest(),resources={'revision':'academy-practical-v2','artifact':artifact,'checks':checks,'capstone':p['_capstone'],'references':[{'title':label,'url':url} for label,url in references]}))

AGENTS=[('Anthropic: workflow and agent architecture patterns','https://www.anthropic.com/engineering/building-effective-agents')]
SECURITY=[('OWASP: risks in LLM applications','https://owasp.org/www-project-top-10-for-large-language-model-applications/')]
TESTS=[('Python unittest reference','https://docs.python.org/3.12/library/unittest.html')]
