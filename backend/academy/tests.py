import json
import zipfile
from io import BytesIO
from pathlib import Path
from django.contrib.auth.models import User
from django.core.management import call_command
from rest_framework.test import APITestCase
from .models import Program, Lesson, Completion, Enrollment, Project, LessonNote

class AcademyTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='learner', password='Sensible-test-password-47')
        self.other = User.objects.create_user(username='other', password='Other-test-password-47')
        self.program = Program.objects.create(slug='test-course', title='Test', category='Cohort', description='Test', audience='Everyone', outcome='Build', duration='28 days')
        self.lesson = Lesson.objects.create(program=self.program, order=0, title='First', module='Basics', content='Learn', task='Try')
    def sign_in(self): self.client.force_authenticate(self.user)
    def test_public_catalog_summaries_and_protected_writes(self):
        response = self.client.get('/api/programs/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('content', response.data[0]['lessons'][0])
        self.assertEqual(self.client.post('/api/programs/test-course/enroll/').status_code, 401)
        self.assertEqual(self.client.get(f'/api/lessons/{self.lesson.pk}/').status_code, 401)
    def test_register_login_logout(self):
        response = self.client.post('/api/auth/register/', {'username':'newstudent','email':'student@example.com','password':'A-unique-build-password-937'})
        self.assertEqual(response.status_code,201)
        token=response.data['token']
        self.assertEqual(self.client.post('/api/auth/login/', {'username':'newstudent','password':'wrong'}).status_code,400)
        self.client.credentials(HTTP_AUTHORIZATION='Token '+token)
        self.assertEqual(self.client.get('/api/me/').status_code,200)
        self.assertEqual(self.client.post('/api/auth/logout/').status_code,204)
        self.assertEqual(self.client.get('/api/me/').status_code,401)
    def test_registration_rejects_bad_inputs(self):
        for body in [{'username':'x','email':'bad','password':'a-safe-password-937'}, {'username':'x','email':'x@example.com','password':'password'}, {'username':'invalid space','email':'x@example.com','password':'a-safe-password-937'}]:
            self.assertEqual(self.client.post('/api/auth/register/',body).status_code,400)
    def test_enroll_complete_undo_idempotent(self):
        self.sign_in()
        route=f'/api/lessons/{self.lesson.pk}/complete/'
        self.assertEqual(self.client.post(route).status_code,403)
        for _ in range(2):self.client.post('/api/programs/test-course/enroll/')
        for _ in range(2):self.client.post(route)
        self.assertEqual(Enrollment.objects.count(),1)
        self.assertEqual(Completion.objects.count(),1)
        self.assertEqual(self.client.get('/api/me/').data['completed'],[self.lesson.pk])
        self.client.delete(route)
        self.assertFalse(Completion.objects.exists())
    def test_private_notes_and_enrolled_reader(self):
        self.sign_in()
        route=f'/api/lessons/{self.lesson.pk}/'
        self.assertEqual(self.client.get(route).status_code,403)
        Enrollment.objects.create(user=self.user,program=self.program)
        self.assertEqual(self.client.put(route+'notes/',{'text':'My finding'},format='json').status_code,200)
        self.assertEqual(self.client.get(route).data['notes'],'My finding')
        self.client.force_authenticate(self.other)
        Enrollment.objects.create(user=self.other,program=self.program)
        self.assertEqual(self.client.get(route).data['notes'],'')
        self.assertEqual(self.client.put(route+'notes/',{'text':'x'*10001},format='json').status_code,400)
    def test_project_ownership_and_template(self):
        self.sign_in()
        response=self.client.post('/api/projects/',{'title':'Research helper','problem':'Summarize public documents'},format='json')
        self.assertEqual(response.status_code,201)
        pk=response.data['id']
        self.assertIn('no AI model',response.data['blueprint']['mode'])
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get('/api/projects/').data,[])
        self.assertEqual(self.client.delete(f'/api/projects/{pk}/').status_code,404)
        self.assertEqual(Project.objects.count(),1)
    def test_terminal_is_bounded_inert_simulation(self):
        self.sign_in()
        self.assertTrue(self.client.post('/api/terminal/',{'command':'pwd'}).data['passed'])
        for cmd in ['rm -rf /','pwd; ls','$(whoami)','python -c "print(1)"']:
            response=self.client.post('/api/terminal/',{'command':cmd})
            self.assertFalse(response.data['passed'])
        self.assertEqual(self.client.post('/api/terminal/',{'command':'a'*201}).status_code,400)
    def test_kit_is_allowlisted_and_protected(self):
        self.assertEqual(self.client.get('/api/learning-kit/').status_code,401)
        self.sign_in()
        response=self.client.get('/api/learning-kit/')
        self.assertEqual(response.status_code,200)
        with zipfile.ZipFile(BytesIO(b''.join(response.streaming_content))) as kit:
            self.assertIn('LICENSE.source',kit.namelist())
            self.assertIn('imported_curriculum.json',kit.namelist())
            self.assertIn('practical_programs.json',kit.namelist())
            self.assertIn('program_labs/tests/test_workflows.py',kit.namelist())
            self.assertEqual(len([n for n in kit.namelist() if n.startswith('program_content/') and n.endswith('.md')]),60)
            self.assertFalse(any(name.endswith(('.env','.sqlite3')) for name in kit.namelist()))

class CurriculumTests(APITestCase):
    def test_full_import_inventory_and_non_overwrite(self):
        call_command('seed_curriculum',verbosity=0)
        call_command('import_workshop',verbosity=0)
        self.assertEqual(Lesson.objects.filter(program__category='Library').count(),523)
        content=Path(__file__).parent/'content'
        provenance=json.loads((content/'provenance.json').read_text())
        self.assertEqual(Lesson.objects.filter(program__category='Accelerator').count(),provenance['accelerator_lessons']+20)
        self.assertEqual(Lesson.objects.filter(program__category='Tutor').count(),8)
        self.assertEqual(Program.objects.count(),25)
        lesson=Lesson.objects.first();lesson.title='Instructor edit';lesson.save()
        call_command('seed_curriculum',verbosity=0)
        call_command('import_workshop',verbosity=0)
        lesson.refresh_from_db();self.assertEqual(lesson.title,'Instructor edit')

class PracticalProgramTests(APITestCase):
    def test_sessions_have_specific_projects_and_practice(self):
        import hashlib
        data=json.loads((Path(__file__).parent/'starter_curriculum.json').read_text())
        self.assertEqual([len(p['lessons']) for p in data],[24,18,18])
        artifacts=[]
        for program in data:
            for lesson in program['lessons']:
                self.assertGreater(len(lesson['content'].split()),250)
                for heading in ['## Worked example','## Build it yourself','## Break it deliberately','## Acceptance checks','## Deliverable']:
                    self.assertIn(heading,lesson['content'])
                self.assertEqual(lesson['content_hash'],hashlib.sha256(lesson['content'].encode()).hexdigest())
                self.assertEqual(len(lesson['resources']['checks']),3)
                artifacts.append(lesson['resources']['artifact'])
        self.assertEqual(len(set(artifacts)),60)
    def test_legacy_upgrade_preserves_history_and_does_not_transfer_completion(self):
        legacy=json.loads((Path(__file__).parent/'legacy_starter_curriculum.json').read_text())[0]
        old_fields={k:v for k,v in legacy.items() if k!='lessons'}
        program=Program.objects.create(**old_fields)
        old=Lesson.objects.create(program=program,**legacy['lessons'][0])
        user=User.objects.create_user(username='legacy-learner')
        Enrollment.objects.create(user=user,program=program)
        Completion.objects.create(user=user,lesson=old)
        LessonNote.objects.create(user=user,lesson=old,text='My original observation')
        old_id=old.pk
        call_command('seed_curriculum',verbosity=0)
        old.refresh_from_db();self.assertEqual(old.pk,old_id)
        self.assertEqual(old.program.category,'Archive')
        self.assertTrue(Completion.objects.filter(user=user,lesson=old).exists())
        self.assertEqual(LessonNote.objects.get(user=user,lesson=old).text,'My original observation')
        self.assertEqual(program.lessons.count(),24)
        self.assertFalse(Completion.objects.filter(user=user,lesson__program=program).exists())
        self.assertTrue(Enrollment.objects.filter(user=user,program=old.program).exists())
        active=program.lessons.first();active.title='Instructor improvement';active.save()
        call_command('seed_curriculum',verbosity=0)
        active.refresh_from_db();self.assertEqual(active.title,'Instructor improvement')
        self.assertEqual(program.lessons.count(),24)
        self.client.force_authenticate(user)
        self.assertNotIn(old_id,self.client.get('/api/me/').data['completed'])
        self.assertFalse(any(p['category']=='Archive' for p in self.client.get('/api/programs/').data))
    def test_course_book_upgrade_preserves_saved_work_and_instructor_edits(self):
        from .models import LessonPractice,QuizAttempt
        old=json.loads((Path(__file__).parent/'current_practical_v3.json').read_text())[0]
        fields={k:v for k,v in old.items() if k!='lessons'}
        program=Program.objects.create(**fields)
        lesson=Lesson.objects.create(program=program,**old['lessons'][0])
        edited=Lesson.objects.create(program=program,**old['lessons'][1])
        edited.content='Instructor-specific explanation';edited.save()
        user=User.objects.create_user(username='book-upgrade')
        Enrollment.objects.create(user=user,program=program)
        LessonNote.objects.create(user=user,lesson=lesson,text='Keep this observation')
        Completion.objects.create(user=user,lesson=lesson)
        prior_revision=lesson.resources['learning']['revision']
        LessonPractice.objects.create(user=user,lesson=lesson,revision=prior_revision,task_evidence='Earlier evidence')
        QuizAttempt.objects.create(user=user,lesson=lesson,revision=prior_revision,answers={},feedback=[],score=2,total=2)
        old_id=lesson.pk
        call_command('seed_curriculum',verbosity=0)
        lesson.refresh_from_db();edited.refresh_from_db()
        self.assertEqual(lesson.pk,old_id)
        self.assertGreater(len(lesson.resources['learning']['chapters']),2)
        self.assertIn('Walk through the mechanism',lesson.content)
        self.assertNotEqual(lesson.resources['learning']['revision'],prior_revision)
        self.assertEqual(LessonNote.objects.get(user=user,lesson=lesson).text,'Keep this observation')
        self.assertTrue(Completion.objects.filter(user=user,lesson=lesson).exists())
        self.assertEqual(LessonPractice.objects.get(user=user,lesson=lesson,revision=prior_revision).task_evidence,'Earlier evidence')
        self.assertEqual(QuizAttempt.objects.get(user=user,lesson=lesson,revision=prior_revision).score,2)
        self.assertEqual(edited.content,'Instructor-specific explanation')
        self.assertEqual(edited.resources['learning']['revision'],old['lessons'][1]['resources']['learning']['revision'])
        self.client.force_authenticate(user)
        summary=self.client.get('/api/programs/').data[0]['lessons'][0]['learning_summary']
        self.assertGreaterEqual(summary['chapters'],3)
        self.assertGreater(summary['quiz'],2)

    def test_health_checks_real_database_and_handles_outage(self):
        from unittest.mock import patch
        from django.db import DatabaseError, connection
        self.assertEqual(self.client.get('/api/health/').data['database'],connection.vendor)
        with patch('rest_framework.throttling.AnonRateThrottle.allow_request',return_value=False):
            self.assertEqual(self.client.get('/api/health/').status_code,200)
        with patch('django.db.connection.cursor',side_effect=DatabaseError('synthetic outage')):
            response=self.client.get('/api/health/')
        self.assertEqual(response.status_code,503)
        self.assertNotIn('synthetic',str(response.data))

class LearningActivityTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_curriculum',verbosity=0)
        cls.program=Program.objects.get(slug='ai-agent-bootcamp')
        cls.lesson=cls.program.lessons.first()
        cls.user=User.objects.create_user(username='activity-student')
        cls.other=User.objects.create_user(username='activity-other')
        Enrollment.objects.create(user=cls.user,program=cls.program)
        Enrollment.objects.create(user=cls.other,program=cls.program)
    def setUp(self):
        self.client.force_authenticate(self.user)
        self.learning=self.lesson.resources['learning']
        self.base=f'/api/lessons/{self.lesson.pk}/'
    def test_learning_inventory_and_independence(self):
        data=json.loads((Path(__file__).parent/'starter_curriculum.json').read_text())
        for program in data:
            for lesson in program['lessons']:
                self.assertNotIn('accelerator',lesson['content'].lower())
                self.assertEqual(len(lesson['resources']['learning']['questions']),3)
                self.assertGreaterEqual(len(lesson['resources']['learning']['chapters']),3)
                self.assertIn('## Before you begin',lesson['content'])
                self.assertIn('## Vocabulary used in this session',lesson['content'])
                self.assertEqual(len(lesson['resources']['learning']['quiz']),3)
                self.assertNotIn('downloadable',lesson['content'])
                for criterion in lesson['resources']['checks']:
                    self.assertIn(criterion,lesson['resources']['learning']['exercise']['material'])
                for concept in lesson['resources']['learning']['concepts']:
                    self.assertIn(concept['definition'],lesson['content'])
                self.assertIn('Inspect the input',lesson['resources']['learning']['exercise']['material'])
                self.assertNotIn('](https://github.com',lesson['content'])
                self.assertIn('MIT License',lesson['resources']['learning']['attribution']['notice'])
                self.assertEqual(len({q['prompt'] for q in lesson['resources']['learning']['quiz']}),len(lesson['resources']['learning']['quiz']))
        response=self.client.get(self.base)
        for question in response.data['resources']['learning']['quiz']:
            self.assertNotIn('correct',question)
            self.assertNotIn('explanation',question)
    def test_server_scoring_and_private_attempts(self):
        correct={q['id']:q['correct'] for q in self.learning['quiz']}
        response=self.client.post(self.base+'quiz/',{'revision':self.learning['revision'],'answers':correct,'score':999},format='json')
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.data['score'],len(self.learning['quiz']))
        self.assertEqual(len(response.data['feedback']),len(self.learning['quiz']))
        self.assertFalse(Completion.objects.filter(user=self.user,lesson=self.lesson).exists())
        wrong={q['id']:next(o['id'] for o in q['options'] if o['id']!=q['correct']) for q in self.learning['quiz']}
        self.assertEqual(self.client.post(self.base+'quiz/',{'revision':self.learning['revision'],'answers':wrong},format='json').data['score'],0)
        state=self.client.get(self.base+'practice/').data
        self.assertEqual(state['best_score'],len(self.learning['quiz']));self.assertEqual(state['attempt_count'],2)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(self.base+'practice/').data['attempt_count'],0)
    def test_saved_reflections_cards_and_conflict(self):
        state=self.client.get(self.base+'practice/').data
        state.update(reflection_answers={'reflection':'My private trade-off'},known_cards=['card-1'])
        saved=self.client.put(self.base+'practice/',state,format='json')
        self.assertEqual(saved.status_code,200)
        self.assertEqual(saved.data['version'],1)
        self.assertEqual(self.client.put(self.base+'practice/',state,format='json').status_code,409)
        self.client.force_authenticate(self.other)
        other=self.client.get(self.base+'practice/').data
        self.assertEqual(other['reflection_answers'],{})
        self.assertEqual(other['known_cards'],[])
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get(self.base+'practice/').data['known_cards'],['card-1'])
    def test_practical_submission_validation(self):
        state=self.client.get(self.base+'practice/').data
        state.update(task_status='submitted',task_evidence='short')
        self.assertEqual(self.client.put(self.base+'practice/',state,format='json').status_code,400)
        state.update(task_evidence='I tested three synthetic policies, recorded supported and unavailable answers, and confirmed the workflow produces drafts only.',checked_criteria=[0,1,2])
        response=self.client.put(self.base+'practice/',state,format='json')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['task_status'],'submitted')
        invalid=dict(response.data,known_cards=['not-a-card'])
        self.assertEqual(self.client.put(self.base+'practice/',invalid,format='json').status_code,400)
        self.assertEqual(self.client.post(self.base+'quiz/',{'revision':'old','answers':{}},format='json').status_code,409)
        self.assertEqual(self.client.post(self.base+'quiz/',{'revision':self.learning['revision'],'answers':{}},format='json').status_code,400)
    def test_enrollment_protects_practice_and_quizzes(self):
        Enrollment.objects.filter(user=self.user).delete()
        self.assertEqual(self.client.get(self.base+'practice/').status_code,403)
        self.assertEqual(self.client.post(self.base+'quiz/',{},format='json').status_code,403)
        self.assertEqual(self.client.get('/api/programs/ai-agent-bootcamp/download/').status_code,403)
    def test_program_download_is_self_contained(self):
        response=self.client.get('/api/programs/ai-agent-bootcamp/download/')
        self.assertEqual(response.status_code,200)
        with zipfile.ZipFile(BytesIO(b''.join(response.streaming_content))) as archive:
            names=archive.namelist()
            self.assertEqual(len([n for n in names if n.startswith('lessons/')]),24)
            self.assertIn('workspace/exercises.py',names)
            self.assertIn('LICENSE.teaching',names)
            self.assertNotIn('imported_curriculum.json',names)
            workbook=json.loads(archive.read('workbook.json'))
            self.assertEqual(len(workbook),24)
            self.assertTrue(all('learning' in row['resources'] for row in workbook))
