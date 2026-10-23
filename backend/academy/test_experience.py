from datetime import timedelta
from unittest.mock import patch
from django.core import mail
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import (Program,Lesson,Enrollment,LabAttempt,ProjectSubmission,LearningPosition,CardReview,LessonQuestion,LessonIssue,LessonNote)
from .labs import lesson_lab

class LearningExperienceTests(APITestCase):
    def setUp(self):
        self.student=User.objects.create_user('student',email='student@example.com',password='Safe-course-password-497!')
        self.other=User.objects.create_user('other',password='Other-password-497!')
        self.staff=User.objects.create_user('reviewer',is_staff=True,password='Staff-password-497!')
        self.program=Program.objects.create(slug='ai-agent-bootcamp',title='Agents',category='Cohort',description='Build',audience='Students',outcome='Agent',duration='8 weeks')
        self.learning={'revision':'lesson-v1','chapters':[{'id':'concept','title':'Scope','body':'Scope guard','kind':'Concept'}], 'concepts':[], 'questions':[], 'flashcards':[{'id':'c1','front':'Boundary?','back':'Fail closed.'}], 'quiz':[{'id':'q1','prompt':'Which?','correct':'a','explanation':'A','options':[{'id':'a','text':'A'},{'id':'b','text':'B'}]}], 'exercise':{'steps':[],'hint':'Check'},'task':{'title':'Scope','deliverable':'guard.py','criteria':[]}}
        self.lesson=Lesson.objects.create(program=self.program,order=0,title='Scope',module='Basics',source_id='academy-v2:ai-agent-bootcamp:01',content='Scope',task='Guard',resources={'learning':self.learning})
        Enrollment.objects.create(user=self.student,program=self.program)
        self.client.force_authenticate(self.student)
        self.base=f'/api/lessons/{self.lesson.pk}/'

    def test_preview_is_public_but_never_contains_private_data(self):
        LessonNote.objects.create(user=self.student,lesson=self.lesson,text='Private note')
        self.client.force_authenticate(None)
        result=self.client.get('/api/programs/ai-agent-bootcamp/preview/')
        self.assertEqual(result.status_code,200)
        self.assertNotIn('notes',result.data)
        self.assertNotIn('correct',result.data['resources']['learning']['quiz'][0])
        self.assertIn('checks',result.data['lab'])
        self.assertEqual(self.client.get(self.base).status_code,401)

    def test_position_requires_enrollment_and_valid_chapter(self):
        self.assertEqual(self.client.put(self.base+'position/',{'chapter':'unknown'},format='json').status_code,400)
        self.assertEqual(self.client.put(self.base+'position/',{'chapter':'concept'},format='json').status_code,200)
        self.assertEqual(self.client.get('/api/me/').data['positions'][self.program.pk]['chapter'],'concept')
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.put(self.base+'position/',{'chapter':'concept'},format='json').status_code,403)
        self.assertEqual(LearningPosition.objects.count(),1)

    def test_notes_conflict_retains_server_copy(self):
        route=self.base+'notes/'
        self.assertEqual(self.client.put(route,{'text':'First','base_text':''},format='json').status_code,200)
        self.assertEqual(self.client.put(route,{'text':'Stale','base_text':''},format='json').status_code,409)
        self.assertEqual(LessonNote.objects.get().text,'First')

    def test_browser_attempts_are_revisioned_and_self_reported(self):
        lab=lesson_lab(self.lesson)
        body={'revision':lab['revision'],'code':lab['solution'],'results':[{'name':c['name'],'passed':True,'detail':'Passed'} for c in lab['checks']]}
        result=self.client.post(self.base+'lab-attempts/',body,format='json')
        self.assertEqual(result.status_code,200)
        self.assertEqual(result.data['verification'],'browser_reported')
        self.assertEqual(self.client.get('/api/me/').data['progress']['lab_passed'],[self.lesson.pk])
        body['results'][0]['name']='forged check'
        self.assertEqual(self.client.post(self.base+'lab-attempts/',body,format='json').status_code,400)
        body['revision']='old'
        self.assertEqual(self.client.post(self.base+'lab-attempts/',body,format='json').status_code,409)
        self.client.force_authenticate(self.other)
        Enrollment.objects.create(user=self.other,program=self.program)
        self.assertIsNone(self.client.get(self.base+'lab-attempts/').data['latest'])
        self.assertEqual(LabAttempt.objects.count(),1)

    def artifact(self):
        return {'artifact_url':'https://example.com/student/project','commit':'abc123','evidence':'Ran the synthetic tests against the declared fixture and recorded observed outputs, failures and remaining limitations.','measurements':{'mode':'offline','latency':'5 ms locally; 10 synthetic runs','cost':'No provider call; not production cost','quality':'3/4 source checks passed','evaluation':'fixtures-v1, tests-v2','context':'Two passages, no cache','limitations':'No load test or cloud deployment'}}

    def test_project_revision_review_and_ownership(self):
        row=self.client.post(self.base+'submissions/',self.artifact(),format='json')
        self.assertEqual(row.status_code,201)
        self.assertEqual(row.data['review_status'],'awaiting_review')
        pk=row.data['id']
        self.assertEqual(self.client.post('/api/reviews/',{'id':pk,'status':'reviewed','feedback':'My own project is good enough to approve myself.'},format='json').status_code,403)
        self.client.force_authenticate(self.other)
        Enrollment.objects.create(user=self.other,program=self.program)
        self.assertEqual(self.client.get(self.base+'submissions/').data,[])
        self.client.force_authenticate(self.staff)
        feedback='Reproduced the exact fixture and verified the scope boundary; factual support still needs a separate human case review.'
        self.assertEqual(self.client.post('/api/reviews/',{'id':pk,'status':'reviewed','feedback':feedback},format='json').status_code,200)
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(self.base+'submissions/').data[0]['reviewer'],'reviewer')
        self.assertEqual(self.client.get('/api/me/').data['progress']['reviewed'],[self.lesson.pk])
        row=self.client.post(self.base+'submissions/',self.artifact(),format='json')
        self.assertEqual(row.status_code,201)
        self.assertEqual(ProjectSubmission.objects.count(),2)
        self.assertEqual(self.client.get(self.base+'submissions/').data[0]['review_status'],'awaiting_review')

    def test_submission_does_not_fetch_urls_or_accept_grading_fields(self):
        data=self.artifact();data['artifact_url']='javascript:alert(1)'
        self.assertEqual(self.client.post(self.base+'submissions/',data,format='json').status_code,400)
        data=self.artifact();data['review_status']='reviewed';data['reviewer']=self.student.pk
        result=self.client.post(self.base+'submissions/',data,format='json')
        self.assertEqual(result.data['review_status'],'awaiting_review')
        self.assertIsNone(result.data['reviewer'])
        data['measurements']['cost']=''
        self.assertEqual(self.client.post(self.base+'submissions/',data,format='json').status_code,400)

    def test_scheduled_review_and_quiz_mistakes(self):
        self.client.get(self.base+'practice/')
        queue=self.client.get('/api/review-queue/').data
        self.assertEqual(len(queue['due_cards']),1)
        self.client.post(self.base+'review-card/',{'card':'c1','rating':'good'},format='json')
        self.assertEqual(self.client.get('/api/review-queue/').data['due_cards'],[])
        row=CardReview.objects.get();self.assertEqual(row.interval_days,3)
        self.client.post(self.base+'review-card/',{'card':'c1','rating':'again'},format='json')
        row.refresh_from_db();self.assertEqual(row.interval_days,0)
        self.assertLess(row.due_at,timezone.now()+timedelta(minutes=11))
        self.client.post(self.base+'quiz/',{'revision':'lesson-v1','answers':{'q1':'b'}},format='json')
        self.assertEqual(len(self.client.get('/api/review-queue/').data['missed_questions']),1)
        self.client.post(self.base+'quiz/',{'revision':'lesson-v1','answers':{'q1':'a'}},format='json')
        self.assertEqual(self.client.get('/api/review-queue/').data['missed_questions'],[])

    def test_help_issues_and_staff_answers(self):
        question=self.client.post(self.base+'questions/',{'question':'Expected a draft; actual refund action. I tried rejecting unknown requests in the scope guard.'},format='json')
        pk=question.data[0]['id']
        self.assertEqual(self.client.post(f'/api/questions/{pk}/answer/',{'answer':'Check the unknown branch before routing.'},format='json').status_code,403)
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.post(f'/api/questions/{pk}/answer/',{'answer':'Check the unknown branch before routing. An unsupported label must fail closed.'},format='json').status_code,200)
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(self.base+'questions/').data[0]['answered_by'],'reviewer')
        self.assertEqual(self.client.post(self.base+'issues/',{'description':'The worked example needs to distinguish action routing from approval.'},format='json').status_code,201)
        self.assertEqual(LessonIssue.objects.get().revision,'lesson-v1')

    def test_learning_plan_validation(self):
        self.assertEqual(self.client.get('/api/learning-plan/').status_code,204)
        body={'goal':'agents','hours_per_week':4,'diagnostic':{'python':'a','http':'b','evaluation':'c'}}
        self.assertEqual(self.client.put('/api/learning-plan/',body,format='json').status_code,200)
        self.assertEqual(self.client.get('/api/learning-plan/').data,body)
        body['hours_per_week']=0
        self.assertEqual(self.client.put('/api/learning-plan/',body,format='json').status_code,400)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',EMAIL_HOST='smtp.example.com',ACADEMY_PUBLIC_URL='http://127.0.0.1:8080')
    def test_password_recovery_private_single_use_and_revokes_token(self):
        import re
        from rest_framework.authtoken.models import Token
        old=Token.objects.create(user=self.student)
        self.client.force_authenticate(None)
        route='/api/auth/password-reset/'
        self.assertEqual(self.client.post(route,{'email':'student@example.com'},format='json').status_code,200)
        self.assertEqual(len(mail.outbox),1)
        uid,token=re.search(r'/#/reset/([^/]+)/([^\s]+)',mail.outbox[0].body).groups()
        body={'uid':uid,'token':token,'password':'New-safe-course-password-519!'}
        self.assertEqual(self.client.post(route+'confirm/',body,format='json').status_code,200)
        self.assertFalse(Token.objects.filter(key=old.key).exists())
        self.assertEqual(self.client.post(route+'confirm/',body,format='json').status_code,400)
        self.assertEqual(self.client.post(route,{'email':'missing@example.com'},format='json').status_code,200)
        self.assertEqual(len(mail.outbox),1)

    def test_authored_reference_labs_pass_and_bad_solutions_fail(self):
        from .labs import LABS
        for spec in LABS.values():
            namespace={};exec(spec['solution'],namespace)
            for name,expression,_ in spec['checks']:
                self.assertTrue(eval(expression,namespace),name)

    def test_sessions_are_real_optional_and_capacity_is_enforced(self):
        from .models import LiveSession,SessionReservation
        session=LiveSession.objects.create(program=self.program,title='Synthetic review session',starts_at=timezone.now()+timedelta(days=1),ends_at=timezone.now()+timedelta(days=1,hours=1),meeting_url='https://example.com/test-session',capacity=1)
        result=self.client.get('/api/sessions/').data
        self.assertIsNone(result[0]['meeting_url'])
        route=f'/api/sessions/{session.pk}/reservation/'
        self.assertEqual(self.client.post(route).status_code,200)
        self.assertEqual(self.client.post(route).status_code,200)
        self.assertEqual(SessionReservation.objects.count(),1)
        self.assertEqual(self.client.get('/api/sessions/').data[0]['meeting_url'],session.meeting_url)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.post(route).status_code,403)
        Enrollment.objects.create(user=self.other,program=self.program)
        self.assertEqual(self.client.post(route).status_code,409)
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.delete(route).status_code,200)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.post(route).status_code,200)

    def test_new_writes_reject_arrays_and_invalid_types(self):
        for route,method in [(self.base+'lab-attempts/','post'),(self.base+'submissions/','post'),(self.base+'questions/','post'),(self.base+'position/','put'),('/api/learning-plan/','put')]:
            self.assertEqual(getattr(self.client,method)(route,[],format='json').status_code,400)
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.post('/api/reviews/',{'id':[]},format='json').status_code,400)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post('/api/auth/password-reset/confirm/',{'uid':[],'token':[]},format='json').status_code,400)

    def test_reference_file_browser_requires_enrollment_and_excludes_runtime_artifacts(self):
        rows=self.client.get('/api/programs/ai-agent-bootcamp/capstone-files/')
        self.assertEqual(rows.status_code,200)
        self.assertTrue(any(row['path']=='app.py' for row in rows.data))
        self.assertFalse(any('observed' in row['path'] or '__pycache__' in row['path'] for row in rows.data))
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get('/api/programs/ai-agent-bootcamp/capstone-files/').status_code,403)
