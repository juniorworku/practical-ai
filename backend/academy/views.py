import shlex
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.throttling import ScopedRateThrottle
from .models import Program, Enrollment, Completion, Lesson, Project, LessonNote
from .serializers import ProgramSerializer, ProjectSerializer, LessonSerializer

class AuthThrottle(ScopedRateThrottle):
    scope = 'auth'
    def allow_request(self, request, view):
        view.throttle_scope = self.scope
        return super().allow_request(request, view)

@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([])
def health(request):
    from django.db import connection, DatabaseError
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except DatabaseError:
        return Response({'status': 'unavailable', 'database': 'unavailable'}, status=503)
    return Response({'status': 'ok', 'database': connection.vendor})

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def register(request):
    username = str(request.data.get('username', '')).strip()
    email = str(request.data.get('email', '')).strip()
    password = request.data.get('password', '')
    if not isinstance(password, str):
        return Response({'detail': 'Password must be text.'}, status=400)
    from rest_framework import serializers
    try:
        email = serializers.EmailField().run_validation(email)
        username = serializers.RegexField(r'^[\w.@+-]{1,150}$').run_validation(username)
        user = User(username=username, email=email)
        validate_password(password, user)
    except (ValidationError, serializers.ValidationError) as exc:
        return Response({'detail': getattr(exc, 'messages', str(exc))}, status=400)
    try:
        with transaction.atomic():
            user.set_password(password); user.save()
            token = Token.objects.create(user=user)
    except IntegrityError:
        return Response({'detail': 'That username is already taken.'}, status=400)
    return Response({'token': token.key, 'username': user.username}, status=201)

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def login(request):
    username, password = request.data.get('username'), request.data.get('password')
    if not isinstance(username, str) or not isinstance(password, str):
        return Response({'detail': 'Username and password must be text.'}, status=400)
    user = authenticate(username=username, password=password)
    if not user: return Response({'detail': 'Username or password is incorrect.'}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'username': user.username})

@api_view(['POST'])
def logout(request):
    request.auth.delete()
    return Response(status=204)

class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Program.objects.prefetch_related('lessons')
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(category='Archive') if self.action == 'list' else queryset
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

@api_view(['GET'])
def dashboard(request):
    from .models import LearningPosition, LessonPractice, QuizAttempt, LabAttempt, ProjectSubmission
    from .labs import lesson_lab
    positions={row.program_id:{'lesson':row.lesson_id,'chapter':row.chapter,'updated_at':row.updated_at.isoformat()} for row in LearningPosition.objects.filter(user=request.user)}
    practiced=list(LessonPractice.objects.filter(user=request.user).exclude(reflection_answers={}, task_evidence='', known_cards=[]).values_list('lesson_id',flat=True).distinct())
    quiz_passed=[]
    for row in QuizAttempt.objects.filter(user=request.user).select_related('lesson'):
        if row.total and row.score==row.total and row.revision==row.lesson.resources.get('learning',{}).get('revision'):
            quiz_passed.append(row.lesson_id)
    lab_passed=[]
    for row in LabAttempt.objects.filter(user=request.user).select_related('lesson__program'):
        lab=lesson_lab(row.lesson)
        if lab and row.revision==lab['revision'] and row.results and all(r['passed'] for r in row.results):lab_passed.append(row.lesson_id)
    reviewed=[row.lesson_id for row in ProjectSubmission.objects.filter(user=request.user,review_status='reviewed').select_related('lesson') if row.revision==row.lesson.resources.get('learning',{}).get('revision',row.lesson.content_hash)]
    return Response({'username':request.user.username,'display_name':request.user.first_name,'is_staff':request.user.is_staff,
        'enrolled':list(Enrollment.objects.filter(user=request.user).exclude(program__category='Archive').values_list('program_id',flat=True)),
        'completed':list(Completion.objects.filter(user=request.user).exclude(lesson__program__category='Archive').values_list('lesson_id',flat=True)),
        'positions':positions,'progress':{'practised':practiced,'quiz_passed':list(set(quiz_passed)),'lab_passed':list(set(lab_passed)),'reviewed':list(set(reviewed))}})


@api_view(['POST'])
def enroll(request, slug):
    program = get_object_or_404(Program, slug=slug)
    _, created = Enrollment.objects.get_or_create(user=request.user, program=program)
    return Response({'program_id': program.id}, status=201 if created else 200)

@api_view(['POST', 'DELETE'])
def complete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if not Enrollment.objects.filter(user=request.user, program=lesson.program).exists():
        return Response({'detail': 'Enroll in this program first.'}, status=403)
    if request.method == 'DELETE':
        Completion.objects.filter(user=request.user, lesson=lesson).delete()
    else: Completion.objects.get_or_create(user=request.user, lesson=lesson)
    return Response({'completed': request.method == 'POST'})

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    def get_queryset(self): return Project.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        title = serializer.validated_data['title']
        problem = serializer.validated_data['problem']
        # Deterministic scaffolding until the owner's original Accelerator is supplied.
        serializer.save(user=self.request.user, blueprint={
            'mode': 'Guided template — no AI model connected',
            'goal': problem,
            'steps': [f'Define a measurable success criterion for {title}.', 'Collect five representative examples; remove personal data.', 'Build a Django REST endpoint and a React input form.', 'Connect a model provider through a server-side adapter.', 'Compare responses with your examples; record failures.', 'Add human review and deploy with Docker.'],
            'deliverables': ['Problem brief', 'Working prototype', 'Evaluation checklist', 'Demo and README']})

@api_view(['POST'])
def terminal(request):
    command = request.data.get('command', '')
    if not isinstance(command, str) or len(command) > 200:
        return Response({'detail': 'Enter a command under 200 characters.'}, status=400)
    try: args = shlex.split(command)
    except ValueError: return Response({'output': 'Unclosed quote. Check your command.', 'hint': 'Close both sides of a quoted string and try again.', 'passed': False, 'mode': 'simulation'})
    outputs = {
        ('pwd',): ('/home/learner/ai-project', 'pwd prints your current directory.'),
        ('ls',): ('README.md  app.py  requirements.txt  data/', 'ls lists files in your current directory.'),
        ('python', '--version'): ('Python 3.12.0 (simulated)', 'Use --version to check your Python installation.'),
        ('mkdir', 'my-agent'): ('Created directory: my-agent (simulated)', 'mkdir creates a directory.'),
        ('cat', 'README.md'): ('# My AI Project\nBuild, evaluate, and share a useful AI workflow.', 'cat displays the contents of a text file.'),
        ('help',): ('Try: pwd, ls, cat README.md, mkdir my-agent, python --version', 'This learning sandbox never executes system commands.')}
    result = outputs.get(tuple(args))
    return Response({'output': result[0] if result else 'Command not available in this sandbox. Type help.', 'hint': result[1] if result else 'Start with pwd to see where you are.', 'passed': bool(result) and tuple(args) != ('help',), 'mode': 'simulation'})

@api_view(['GET'])
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if not Enrollment.objects.filter(user=request.user, program=lesson.program).exists():
        return Response({'detail': 'Enroll in this program first.'}, status=403)
    result = LessonSerializer(lesson).data
    result['notes'] = LessonNote.objects.filter(user=request.user, lesson=lesson).values_list('text', flat=True).first() or ''
    return Response(result)

@api_view(['PUT'])
def save_note(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if not Enrollment.objects.filter(user=request.user, program=lesson.program).exists():
        return Response({'detail': 'Enroll in this program first.'}, status=403)
    text = request.data.get('text', '')
    if not isinstance(text, str) or len(text) > 10000:
        return Response({'detail': 'Notes must be text under 10,000 characters.'}, status=400)
    with transaction.atomic():
        note,_ = LessonNote.objects.get_or_create(user=request.user, lesson=lesson)
        note = LessonNote.objects.select_for_update().get(pk=note.pk)
        if 'base_text' in request.data and request.data['base_text'] != note.text:
            return Response({'detail':'Notes changed in another session. Your local draft is retained; copy it before reloading.'},status=409)
        note.text=text;note.save()
    return Response({'saved': True})

@api_view(['GET'])
def course_download(request):
    from django.http import FileResponse
    from django.conf import settings
    return FileResponse(open(settings.BASE_DIR / 'academy' / 'content' / 'workshop-learning-kit.zip', 'rb'), as_attachment=True, filename='practical-ai-learning-kit.zip')
