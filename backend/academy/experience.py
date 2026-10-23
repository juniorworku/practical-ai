"""Learning workflow endpoints. Code execution happens in the browser only."""
import logging
import smtplib
from datetime import timedelta
from django.contrib.auth.forms import SetPasswordForm
from .recovery import RecoveryForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import (Lesson, Program, Enrollment, LearningPosition, LabAttempt, ProjectSubmission,
                     CardReview, LessonQuestion, LessonIssue, LearningPlan)
from .serializers import LessonSerializer
from .labs import lesson_lab
from .views import AuthThrottle


def enrolled(request, pk):
    lesson = get_object_or_404(Lesson.objects.select_related('program'), pk=pk)
    if not Enrollment.objects.filter(user=request.user, program=lesson.program).exists():
        return lesson, Response({'detail': 'Enroll in this program first.'}, status=403)
    return lesson, None


def text(value, minimum=0, maximum=4000):
    return isinstance(value, str) and minimum <= len(value.strip()) and len(value) <= maximum


def revision(lesson):
    return lesson.resources.get('learning', {}).get('revision', lesson.content_hash)


@api_view(['GET'])
@permission_classes([AllowAny])
def preview(request, slug):
    lesson = get_object_or_404(Lesson.objects.select_related('program'), program__slug=slug, order=0)
    if lesson.program.category in ['Archive','Library']:
        return Response({'detail':'Preview unavailable.'}, status=404)
    return Response(LessonSerializer(lesson).data)


@api_view(['PUT'])
def position(request, pk):
    if request.method in ['POST','PUT'] and not isinstance(request.data,dict):
        return Response({'detail':'Send a JSON object.'},status=400)
    lesson, error = enrolled(request, pk)
    if error is not None: return error
    chapter = request.data.get('chapter', '')
    ids = {c['id'] for c in lesson.resources.get('learning', {}).get('chapters', [])}
    if not isinstance(chapter, str) or (chapter and chapter not in ids):
        return Response({'detail':'Choose a chapter from this lesson.'}, status=400)
    LearningPosition.objects.update_or_create(user=request.user, program=lesson.program, defaults={'lesson':lesson,'chapter':chapter})
    return Response({'lesson':lesson.pk,'chapter':chapter})


@api_view(['GET','POST'])
def lab_attempts(request, pk):
    if request.method in ['POST','PUT'] and not isinstance(request.data,dict):
        return Response({'detail':'Send a JSON object.'},status=400)
    lesson, error = enrolled(request, pk)
    if error is not None: return error
    lab = lesson_lab(lesson)
    if not lab: return Response({'detail':'No browser lab for this lesson.'}, status=404)
    rows = LabAttempt.objects.filter(user=request.user, lesson=lesson, revision=lab['revision'])
    if request.method == 'POST':
        data=request.data
        checks=data.get('results')
        if data.get('revision') != lab['revision']:
            return Response({'detail':'This lab changed. Reload before saving.'}, status=409)
        if not text(data.get('code'),1,20000) or not isinstance(checks,list) or len(checks)!=len(lab['checks']) or any(not isinstance(row,dict) or row.get('name')!=expected['name'] or type(row.get('passed')) is not bool or not text(row.get('detail',''),0,2000) for row,expected in zip(checks,lab['checks'])):
            return Response({'detail':'Send code and a result for each named lab check.'}, status=400)
        LabAttempt.objects.create(user=request.user, lesson=lesson, revision=lab['revision'], code=data['code'], results=[{'name':r['name'],'passed':r['passed'],'detail':r.get('detail','')} for r in checks])
    latest=rows.first()
    return Response({'attempts':rows.count(),'latest': {'id':latest.pk,'code':latest.code,'results':latest.results,'created_at':latest.created_at} if latest else None, 'verification':'browser_reported'})


def submission_data(row):
    return {**{k:getattr(row,k) for k in ['id','artifact_url','commit','evidence','measurements','review_status','review_feedback','created_at','revision']},'reviewer':row.reviewer.username if row.reviewer else None,'reviewed_at':row.reviewed_at}


@api_view(['GET','POST'])
def submissions(request, pk):
    if request.method in ['POST','PUT'] and not isinstance(request.data,dict):
        return Response({'detail':'Send a JSON object.'},status=400)
    lesson, error = enrolled(request, pk)
    if error is not None: return error
    if request.method=='POST':
        data=request.data
        try: URLValidator(schemes=['https','http'])(data.get('artifact_url',''))
        except (ValidationError,TypeError): return Response({'detail':'Provide an http(s) artifact or repository URL. The academy does not fetch this URL.'},status=400)
        metrics=data.get('measurements',{})
        if not text(data.get('artifact_url'),1,1000) or not text(data.get('commit',''),0,80) or not text(data.get('evidence'),80,12000) or not isinstance(metrics,dict) or set(metrics)!={'mode','latency','cost','quality','evaluation','context','limitations'} or any(not text(v,1,2000) for v in metrics.values()) or metrics['mode'] not in ['offline','live','mixed']:
            return Response({'detail':'Include evidence (80+ characters) and every engineering measurement. State unmeasured values explicitly.'},status=400)
        row=ProjectSubmission.objects.create(user=request.user,lesson=lesson,revision=revision(lesson),artifact_url=data['artifact_url'],commit=data.get('commit',''),evidence=data['evidence'],measurements=metrics)
        return Response(submission_data(row),status=201)
    return Response([submission_data(r) for r in ProjectSubmission.objects.filter(user=request.user,lesson=lesson).select_related('reviewer')[:30]])


@api_view(['GET','POST'])
def reviews(request):
    if request.method in ['POST','PUT'] and not isinstance(request.data,dict):
        return Response({'detail':'Send a JSON object.'},status=400)
    if not request.user.is_staff: return Response({'detail':'Reviewer access required.'},status=403)
    if request.method=='POST':
        if type(request.data.get('id')) is not int:
            return Response({'detail':'Provide a submission ID.'},status=400)
        with transaction.atomic():
            row=get_object_or_404(ProjectSubmission.objects.select_for_update(),pk=request.data['id'])
            if row.user_id==request.user.pk: return Response({'detail':'You cannot review your own submission.'},status=400)
            status=request.data.get('status')
            feedback=request.data.get('feedback')
            if status not in ['reviewed','changes_requested'] or not text(feedback,40,12000):
                return Response({'detail':'Choose a review outcome and provide at least 40 characters of actionable feedback.'},status=400)
            row.review_status=status;row.review_feedback=feedback;row.reviewer=request.user;row.reviewed_at=timezone.now();row.save()
            return Response(submission_data(row))
    return Response([{**submission_data(row),'student':row.user.username,'lesson':row.lesson.title,'lesson_id':row.lesson_id} for row in ProjectSubmission.objects.select_related('user','lesson','reviewer').filter(review_status='awaiting_review')[:100]])


@api_view(['POST'])
def review_card(request, pk):
    if request.method in ['POST','PUT'] and not isinstance(request.data,dict):
        return Response({'detail':'Send a JSON object.'},status=400)
    lesson,error=enrolled(request,pk)
    if error is not None:return error
    learning=lesson.resources.get('learning',{})
    card=request.data.get('card');rating=request.data.get('rating')
    if card not in [c['id'] for c in learning.get('flashcards',[])] or rating not in ['again','hard','good']:
        return Response({'detail':'Choose a lesson card and again, hard or good.'},status=400)
    with transaction.atomic():
        row,_=CardReview.objects.get_or_create(user=request.user,lesson=lesson,revision=revision(lesson),card=card,defaults={'due_at':timezone.now()})
        row=CardReview.objects.select_for_update().get(pk=row.pk)
        row.interval_days=0 if rating=='again' else 1 if rating=='hard' else min(30,max(3,row.interval_days*2))
        row.due_at=timezone.now()+(timedelta(minutes=10) if rating=='again' else timedelta(days=row.interval_days));row.save()
    return Response({'due_at':row.due_at,'interval_days':row.interval_days})


@api_view(['GET'])
def review_queue(request):
    from .models import LessonPractice, QuizAttempt
    positions={row.program_id:row for row in LearningPosition.objects.filter(user=request.user).select_related('lesson')}
    due=[];missed=[]
    schedules={(row.lesson_id,row.revision,row.card):row for row in CardReview.objects.filter(user=request.user)}
    latest_attempts={}
    for attempt in QuizAttempt.objects.filter(user=request.user):
        latest_attempts.setdefault((attempt.lesson_id,attempt.revision),attempt)
    states=LessonPractice.objects.filter(user=request.user,lesson__program__enrollment__user=request.user).select_related('lesson__program').order_by('-updated_at')
    for state in states:
        learning=state.lesson.resources.get('learning',{})
        if state.revision!=learning.get('revision'):continue
        for card in learning.get('flashcards',[]):
            row=schedules.get((state.lesson_id,state.revision,card['id']))
            if row is None or row.due_at<=timezone.now():due.append({'lesson':state.lesson_id,'program':state.lesson.program.slug,**card})
        attempt=latest_attempts.get((state.lesson_id,state.revision))
        if attempt:
            for feedback in attempt.feedback:
                if not feedback['correct']:missed.append({'lesson':state.lesson_id,'program':state.lesson.program.slug,'title':state.lesson.title,'question':next(q['prompt'] for q in learning['quiz'] if q['id']==feedback['id'])})
    return Response({'due_cards':due[:30],'missed_questions':missed[:20],'positions':{key:{'lesson':row.lesson_id,'chapter':row.chapter} for key,row in positions.items()}})


@api_view(['GET','POST'])
def questions(request, pk):
    if request.method in ['POST','PUT'] and not isinstance(request.data,dict):
        return Response({'detail':'Send a JSON object.'},status=400)
    lesson,error=enrolled(request,pk)
    if error is not None:return error
    if request.method=='POST':
        if not text(request.data.get('question'),30,4000):return Response({'detail':'Describe the expected result, actual result and what you tried (30–4000 characters).'},status=400)
        LessonQuestion.objects.create(user=request.user,lesson=lesson,question=request.data['question'])
    return Response([{'id':row.pk,'author':row.user.username,'question':row.question,'answer':row.answer,'answered_by':row.answered_by.username if row.answered_by else None,'created_at':row.created_at} for row in LessonQuestion.objects.filter(lesson=lesson).select_related('user','answered_by')[:50]])


@api_view(['POST'])
def answer_question(request, pk):
    if request.method in ['POST','PUT'] and not isinstance(request.data,dict):
        return Response({'detail':'Send a JSON object.'},status=400)
    if not request.user.is_staff:return Response({'detail':'Reviewer access required.'},status=403)
    row=get_object_or_404(LessonQuestion,pk=pk)
    if not text(request.data.get('answer'),20,6000):return Response({'detail':'Provide a useful explanation (20–6000 characters).'},status=400)
    row.answer=request.data['answer'];row.answered_by=request.user;row.save()
    return Response({'saved':True})


@api_view(['POST'])
def report_issue(request, pk):
    if request.method in ['POST','PUT'] and not isinstance(request.data,dict):
        return Response({'detail':'Send a JSON object.'},status=400)
    lesson,error=enrolled(request,pk)
    if error is not None:return error
    if not text(request.data.get('description'),20,4000):return Response({'detail':'Describe the unclear concept or broken example (20–4000 characters).'},status=400)
    LessonIssue.objects.create(user=request.user,lesson=lesson,revision=revision(lesson),description=request.data['description'])
    return Response({'saved':True},status=201)


@api_view(['GET','PUT'])
def learning_plan(request):
    if request.method in ['POST','PUT'] and not isinstance(request.data,dict):
        return Response({'detail':'Send a JSON object.'},status=400)
    row=LearningPlan.objects.filter(user=request.user).first()
    if request.method=='PUT':
        goal=request.data.get('goal');hours=request.data.get('hours_per_week');diagnostic=request.data.get('diagnostic')
        if goal not in ['workflow','agents','engineering','freelancing','foundations'] or type(hours) is not int or not 1<=hours<=40 or not isinstance(diagnostic,dict) or set(diagnostic)!={'python','http','evaluation'} or any(v not in ['a','b','c'] for v in diagnostic.values()):
            return Response({'detail':'Choose a goal, 1–40 weekly hours and answer all three diagnostic questions.'},status=400)
        row,_=LearningPlan.objects.update_or_create(user=request.user,defaults={'goal':goal,'hours_per_week':hours,'diagnostic':diagnostic})
    if row is None:return Response(status=204)
    return Response({'goal':row.goal,'hours_per_week':row.hours_per_week,'diagnostic':row.diagnostic})


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def reset_request(request):
    if request.method in ['POST','PUT'] and not isinstance(request.data,dict):
        return Response({'detail':'Send a JSON object.'},status=400)
    form=RecoveryForm(request.data)
    if not form.is_valid():return Response({'detail':'Enter a valid email address.'},status=400)
    if settings.EMAIL_HOST:
        try:
            form.save(use_https=settings.ACADEMY_PUBLIC_URL.startswith('https:'),domain_override=settings.ACADEMY_PUBLIC_URL.split('://',1)[1],email_template_name='academy/password_reset_email.txt',subject_template_name='academy/password_reset_subject.txt',html_email_template_name='academy/password_reset_email.html')
        except (OSError, smtplib.SMTPException):
            logging.getLogger(__name__).warning('Password recovery delivery failed; check SMTP configuration.')
    return Response({'detail':'If an account matches that email, a recovery message will be sent. If it does not arrive, contact the academy administrator.'})


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def reset_confirm(request):
    if request.method in ['POST','PUT'] and not isinstance(request.data,dict):
        return Response({'detail':'Send a JSON object.'},status=400)
    if not isinstance(request.data.get('uid'),str) or not isinstance(request.data.get('token'),str):
        return Response({'detail':'This recovery link is invalid.'},status=400)
    try:user=User.objects.get(pk=force_str(urlsafe_base64_decode(request.data.get('uid',''))))
    except (ValueError,TypeError,OverflowError,User.DoesNotExist):user=None
    if user is None or not default_token_generator.check_token(user,request.data.get('token','')):
        return Response({'detail':'This recovery link expired or is invalid. Request another one.'},status=400)
    form=SetPasswordForm(user,{'new_password1':request.data.get('password'),'new_password2':request.data.get('password')})
    if not form.is_valid():return Response({'detail':list(form.errors.values())},status=400)
    form.save()
    from django.contrib.sessions.models import Session
    from .models import AccountSession
    Session.objects.filter(session_key__in=AccountSession.objects.filter(user=user).values('session_key')).delete()
    AccountSession.objects.filter(user=user).delete()
    user.auth_token.delete() if hasattr(user,'auth_token') else None
    return Response({'detail':'Password updated. Log in with your new password.'})

@api_view(['GET'])
def capstone_files(request, slug):
    from pathlib import Path
    program=get_object_or_404(Program,slug=slug)
    if not Enrollment.objects.filter(user=request.user,program=program).exists():
        return Response({'detail':'Enroll in this program first.'},status=403)
    folder=Path(settings.BASE_DIR)/'academy'/'content'/'capstones'/program.slug
    files=[]
    suffixes={'.py','.md','.txt','.json','.jsonl','.yaml','.toml','.sql','.html','.csv','.ini'}
    if folder.is_dir():
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or path.is_symlink() or any(part in ['__pycache__','.venv','.git'] for part in path.parts):continue
            if path.suffix not in suffixes and path.name not in ['Dockerfile','.dockerignore']:continue
            if path.name.startswith('observed') or path.name.endswith('-observed.json'):continue
            if path.stat().st_size>100000:continue
            files.append({'path':str(path.relative_to(folder)),'content':path.read_text()})
    return Response(files)


@api_view(['GET'])
def sessions(request):
    from .models import LiveSession, SessionReservation
    rows=LiveSession.objects.filter(program__enrollment__user=request.user,starts_at__gt=timezone.now()).select_related('program')[:50]
    own=set(SessionReservation.objects.filter(user=request.user).values_list('session_id',flat=True))
    return Response([{'id':row.pk,'program':row.program.title,'title':row.title,'starts_at':row.starts_at,'ends_at':row.ends_at,'reserved':row.pk in own,'places_left':max(0,row.capacity-row.reservations.count()),'meeting_url':row.meeting_url if row.pk in own else None} for row in rows])


@api_view(['POST','DELETE'])
def reserve_session(request, pk):
    from .models import LiveSession, SessionReservation
    with transaction.atomic():
        row=get_object_or_404(LiveSession.objects.select_for_update(),pk=pk)
        if not Enrollment.objects.filter(user=request.user,program=row.program).exists():return Response({'detail':'Enroll in this session’s program first.'},status=403)
        if request.method=='DELETE':
            SessionReservation.objects.filter(user=request.user,session=row).delete()
            return Response({'reserved':False})
        if row.starts_at<=timezone.now():return Response({'detail':'This session has already started.'},status=400)
        if not SessionReservation.objects.filter(user=request.user,session=row).exists():
            if row.reservations.count()>=row.capacity:return Response({'detail':'This session is full.'},status=409)
            SessionReservation.objects.create(user=request.user,session=row)
    return Response({'reserved':True})
