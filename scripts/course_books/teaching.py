"""Turn the reviewed baseline into teach → trace → practice → feedback."""
import subprocess,sys,tempfile
from pathlib import Path
from .student_guides import GUIDES
from .feedback import REASONS

def fence(kind,text):return '```'+kind+'\n'+text.strip()+'\n```'
def strengthen(key,learning,chapters,fixture_why,variation):
    from .student_labs import LABS
    from .build import docker_instructions
    guide=GUIDES[key];business=key.startswith('F')
    original_steps=list(learning['exercise']['steps']);original_criteria=list(learning['task']['criteria'])
    tutorial={'id':'concept-tutorial','title':'Learn each concept step by step','kind':'Guided concept teaching',
      'body':'Work through these explanations before the completed example or exercise. Follow the inputs, mechanism and decision boundary rather than memorizing the definitions.\n\n'+'\n\n'.join('## Step '+str(i+1)+' · '+concept['term']+'\n\n'+explanation for i,(concept,explanation) in enumerate(zip(learning['concepts'],guide['explanations'])))}
    chapters.insert(1,tutorial)
    worked=next(c for c in chapters if c['id']=='worked-implementation')
    walkthrough='## Walk through the data and decision\n\n'+'\n\n'.join(str(i+1)+'. '+text for i,text in enumerate(guide['trace']))
    worked['body']=walkthrough+'\n\n'+worked['body']
    if business:
        reference='## Complete guided-practice reference\n\nAttempt the changed case first, then compare your reasoning with this completed response. This is a worked decision under stated assumptions, not evidence of performed client work.\n\n'+guide['reference']
        code=guide['extension']
    else:
        code=LABS[key]['code']+'\n# Complete guided-practice reference change\n'+guide['extension']+'\n'
        reference='## Complete guided-practice reference\n\nSave the entire block as solution.py in a new scratch directory. Use Python 3.12 and run `python3 -I solution.py` with assertions enabled. All imports and synthetic data are included. The Python checks use the standard library and no provider account. This reference covers the bounded practice, not the completed integration project.\n\n'
    if code:
        with tempfile.TemporaryDirectory(prefix='academy-practice-reference-') as folder:
            file=Path(folder)/'solution.py';file.write_text(code)
            result=subprocess.run([sys.executable,'-I',str(file)],cwd=folder,capture_output=True,text=True,timeout=15,check=True)
        reference+='\n\n'+fence('python',code)+'\n\n## Expected reference observation\n\n'+fence('text',result.stdout)
    if key=='B19':
        reference+='\n\n## Complete the Docker part of this practice\n\nThe Python generator only prepares the files. It does not run Docker or pass the persistence/outage gates. Inspect the complete files in the lesson, then follow this procedure and record actual responses.\n\n'+docker_instructions()
    reference+='\n\n## If your result differs\n\n'+guide['diagnosis']+'\n\n## Explain before continuing\n\nName the decision or invariant your change protects. Compare the baseline with your result, retain the failed case, and state what remains untested in the larger project.'
    steps=['Read the concept tutorial and trace the completed baseline/specimen before attempting a change.',guide['task'],
           'Make your own attempt, record the normal and counterexample outcomes, then compare with the complete reference and diagnostic feedback.',
           'After the bounded practice, extend your own project using the integration steps and acceptance checks below.']
    criteria=['The completed baseline/specimen is explained using the lesson walkthrough, with fixture assumptions distinguished from observations.',guide['task'],
              'The decision and counterexample are recorded with evidence and remaining uncertainty; simulated and observed results are labeled.' if business else 'The implementation includes positive and negative checks, actual output and explicit limits on what those checks establish.']
    learning['exercise']={'steps':steps,'hint':guide['hints'][0],'hints':guide['hints'],'solution':reference,
      'material':walkthrough+'\n\n## 1. Inspect the input and predict the outcome\n\n'+learning['exercise']['material'].split('### 1. Inspect the input and predict the outcome',1)[-1].split('### 4. Make the targeted change',1)[0]+'\n\n## Bounded first practice\n\n'+guide['task']+'\n\n## Practice sequence\n\n'+'\n'.join(str(i+1)+'. '+s for i,s in enumerate(steps))+'\n\n## What to submit and check\n\n'+'\n'.join('- '+c for c in criteria)+'\n\n## Next: integration work\n\n'+'\n'.join(str(i+1)+'. '+s for i,s in enumerate(original_steps))+'\n\n## Integration acceptance\n\n'+'\n'.join('- '+c for c in original_criteria)+'\n\n## Further challenge\n\n'+variation}
    project=next(c for c in chapters if c['id']=='case-study')
    project['title']='Practice first, then integrate'
    project['body']='## Bounded first practice\n\n'+guide['task']+'\n\n## Practice acceptance\n\n'+'\n'.join('- '+c for c in criteria)+'\n\n## Integrate after practice\n\n'+project['body']+'\n\n## Full project sequence\n\n'+'\n'.join(str(i+1)+'. '+s for i,s in enumerate(original_steps))+'\n\n## Integration acceptance\n\n'+'\n'.join('- '+c for c in original_criteria)
    learning['task']['criteria']=criteria
    reflection=learning['questions'][0]
    learning['questions']=[
      {**reflection,'guidance':guide['explanations'][0]+' Apply it to the specific input and observation: '+guide['trace'][0]},
      {'id':'diagnosis','prompt':guide['task'],'guidance':guide['diagnosis']},
      {'id':'transfer','prompt':variation,'guidance':fixture_why+' '+guide['explanations'][2]}]
    for question in learning['quiz']:
        if question['id']=='concept':
            definition=next(o['text'] for o in question['options'] if o['id']==question['correct'])
            feedback={}
            for option in question['options']:
                if option['id']==question['correct']:reason='Correct: '+definition
                else:reason='This describes '+next(c['term'] for c in learning['concepts'] if c['definition']==option['text'])+', rather than '+learning['concepts'][0]['term']+'.'
                feedback[option['id']]=reason+' '+guide['explanations'][0]
        else:
            wrongs=[o for o in question['options'] if o['id']!=question['correct']]
            reasons={o['id']:reason for o,reason in zip(wrongs,REASONS[key][question['id']])}
            feedback={o['id']:('Correct: '+o['text'] if o['id']==question['correct'] else 'Why this choice fails: '+reasons[o['id']])+'\n\nNext check: '+(guide['trace'][0] if question['id']=='scenario' else guide['diagnosis']) for o in question['options']}
        question['option_feedback']=feedback
    return guide
