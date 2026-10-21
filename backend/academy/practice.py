import json
import zipfile
from io import BytesIO
from pathlib import Path
from django.conf import settings
from django.db import transaction
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Lesson, Program, Enrollment, LessonPractice, QuizAttempt


def get_learning(request, pk):
    lesson=get_object_or_404(Lesson,pk=pk)
    if not Enrollment.objects.filter(user=request.user,program=lesson.program).exists():
        return None,None,Response({'detail':'Enroll in this program first.'},status=403)
    learning=lesson.resources.get('learning')
    if not learning:
        return None,None,Response({'detail':'This lesson uses its original course reader.'},status=404)
    return lesson,learning,None

def attempt_data(attempt):
    return {'id':attempt.pk,'score':attempt.score,'total':attempt.total,'answers':attempt.answers,'feedback':attempt.feedback,'created_at':attempt.created_at.isoformat()}

def state_data(state):
    return {key:getattr(state,key) for key in ['revision','reflection_answers','known_cards','task_evidence','checked_criteria','task_status','version']}

@api_view(['GET','PUT'])
def practice_state(request,pk):
    lesson,learning,error=get_learning(request,pk)
    if error is not None:return error
    with transaction.atomic():
        state,_=LessonPractice.objects.get_or_create(user=request.user,lesson=lesson,revision=learning['revision'])
        if request.method=='PUT':
            state=LessonPractice.objects.select_for_update().get(pk=state.pk)
            data=request.data
            if not isinstance(data,dict):return Response({'detail':'Send a JSON object.'},status=400)
            if data.get('revision')!=state.revision or data.get('version')!=state.version:
                return Response({'detail':'Your saved practice changed. Reload before saving again; copy your draft first.'},status=409)
            answers=data.get('reflection_answers',state.reflection_answers)
            cards=data.get('known_cards',state.known_cards)
            checked=data.get('checked_criteria',state.checked_criteria)
            evidence=data.get('task_evidence',state.task_evidence)
            status=data.get('task_status',state.task_status)
            question_ids={q['id'] for q in learning['questions']}
            card_ids={c['id'] for c in learning['flashcards']}
            count=len(learning['task']['criteria'])
            valid=(isinstance(answers,dict) and set(answers)<=question_ids and all(isinstance(v,str) and len(v)<=6000 for v in answers.values())
                and isinstance(cards,list) and all(isinstance(v,str) for v in cards) and set(cards)<=card_ids and len(cards)==len(set(cards))
                and isinstance(checked,list) and all(type(v) is int and 0<=v<count for v in checked) and len(checked)==len(set(checked))
                and isinstance(evidence,str) and len(evidence)<=12000 and status in ['draft','submitted'])
            if not valid:return Response({'detail':'Practice contains invalid fields or exceeds the text limits.'},status=400)
            if status=='submitted' and (len(evidence.strip())<80 or set(checked)!=set(range(count))):
                return Response({'detail':'To submit, describe your observed work in at least 80 characters and check every acceptance criterion.'},status=400)
            for key,value in [('reflection_answers',answers),('known_cards',cards),('checked_criteria',checked),('task_evidence',evidence),('task_status',status)]:setattr(state,key,value)
            state.version+=1;state.save()
        result=state_data(state)
    attempts=QuizAttempt.objects.filter(user=request.user,lesson=lesson,revision=learning['revision'])
    latest=attempts.first()
    result.update(last_quiz=attempt_data(latest) if latest else None,best_score=max(attempts.values_list('score',flat=True),default=0),attempt_count=attempts.count())
    return Response(result)

@api_view(['POST'])
def submit_quiz(request,pk):
    lesson,learning,error=get_learning(request,pk)
    if error is not None:return error
    if not isinstance(request.data,dict):return Response({'detail':'Send a JSON object.'},status=400)
    if request.data.get('revision')!=learning['revision']:
        return Response({'detail':'This quiz revision changed. Reload the lesson before submitting.'},status=409)
    answers=request.data.get('answers')
    questions=learning['quiz']
    if not isinstance(answers,dict) or set(answers)!={q['id'] for q in questions}:
        return Response({'detail':'Answer every question before submitting.'},status=400)
    feedback=[]
    for question in questions:
        selected=answers[question['id']]
        if not isinstance(selected,str) or selected not in {c['id'] for c in question['options']}:
            return Response({'detail':'Select one of the supplied options for each question.'},status=400)
        feedback.append({'id':question['id'],'correct':selected==question['correct'],'selected':selected,'correct_option':question['correct'],'explanation':question.get('option_feedback',{}).get(selected,question['explanation'])})
    attempt=QuizAttempt.objects.create(user=request.user,lesson=lesson,revision=learning['revision'],answers=answers,feedback=feedback,score=sum(f['correct'] for f in feedback),total=len(questions))
    return Response(attempt_data(attempt),status=201)

@api_view(['GET'])
def program_download(request,slug):
    program=get_object_or_404(Program,slug=slug)
    if not Enrollment.objects.filter(user=request.user,program=program).exists():
        return Response({'detail':'Enroll in this program before downloading its workbook.'},status=403)
    base=Path(settings.BASE_DIR)/'academy'
    output=BytesIO()
    safe_suffixes={'.md','.py','.json','.jsonl','.toml','.lock','.txt','.csv','.html','.sql','.yaml','.ini'}
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('LICENSE.teaching',(base/'content/LICENSE.source').read_text())
        archive.writestr('README.md',f'# {program.title}\n\nAn independent learning workspace for this program. Work locally with synthetic data. Lessons, questions, quizzes, flashcards, exercises and practical tasks belong to this program. Downloaded quiz solutions are self-study references, not evidence of a passed online attempt.\n')
        rows=[]
        for lesson in program.lessons.all():
            archive.writestr(f'lessons/{lesson.order+1:02}.md',lesson.content)
            rows.append({'title':lesson.title,'module':lesson.module,'minutes':lesson.minutes,'task':lesson.task,'resources':lesson.resources})
        archive.writestr('workbook.json',json.dumps(rows,indent=2))
        folder=base/'content'/('starter' if program.category=='Accelerator' else 'engineering_examples' if program.category=='Engineering' else 'program_labs')
        if program.category in ['Cohort','Workshop','Masterclass','Accelerator','Engineering']:
            for path in folder.rglob('*'):
                if path.is_file() and not any(part in ['__pycache__','.venv','.pytest_cache','.git'] for part in path.parts) and (path.suffix in safe_suffixes or path.name.startswith('LICENSE')):
                    archive.write(path,'workspace/'+str(path.relative_to(folder)))
        if program.category in ['Accelerator','Tutor']:
            for path in (base/'content/reviewed_examples').glob('*.py'):
                if path.stem.startswith('terminal-') == (program.category=='Tutor'):
                    archive.write(path,'reference_examples/'+path.name)
        if program.category=='Accelerator':
            for path in (base/'content/accelerator_stack').rglob('*'):
                if path.is_file() and '__pycache__' not in path.parts and (path.suffix in safe_suffixes or path.name in ['Dockerfile','.dockerignore']):
                    archive.write(path,'accelerator_stack/'+str(path.relative_to(base/'content/accelerator_stack')))
        capstone=base/'content/capstones'/program.slug
        if capstone.is_dir():
            for path in capstone.rglob('*'):
                if path.is_file() and not any(part in ['__pycache__','.venv','.git'] for part in path.parts) and not path.name.startswith('observed') and not path.name.endswith('-observed.json') and (path.suffix in safe_suffixes or path.name in ['Dockerfile','.dockerignore']):
                    archive.write(path,'capstone/'+str(path.relative_to(capstone)))
        if program.category=='Accelerator':archive.write(base/'content/LICENSE.accelerator','LICENSE.upstream')
    output.seek(0)
    return FileResponse(output,as_attachment=True,filename=program.slug+'-workbook.zip')
