from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from .models import AccountSession, Program, Lesson, Enrollment, LessonNote, ProjectSubmission

class BrowserAccountsTests(APITestCase):
    password='Course-password-5729!'
    def setUp(self):
        cache.clear()
        self.user=User.objects.create_user('builder',email='builder@example.com',password=self.password)
        self.client=APIClient(enforce_csrf_checks=True)
    def csrf(self,client=None):
        client=client or self.client
        self.assertEqual(client.get('/api/auth/session/').status_code,200)
        return {'HTTP_X_CSRFTOKEN':client.cookies['csrftoken'].value}
    def sign_in(self,client=None,**data):
        client=client or self.client
        return client.post('/api/auth/session/login/',{'username':'builder','password':self.password,**data},format='json',**self.csrf(client))
    def test_login_requires_csrf_even_when_anonymous(self):
        self.assertEqual(self.client.post('/api/auth/session/login/',{'username':'builder','password':self.password},format='json').status_code,403)
        self.assertEqual(self.client.post('/api/auth/session/register/',{'username':'new'},format='json').status_code,403)
    def test_cookie_login_email_case_remember_and_private_session(self):
        result=self.sign_in(username='BUILDER@EXAMPLE.COM',remember=True)
        self.assertEqual(result.status_code,200)
        self.assertNotIn('token',result.data)
        self.assertTrue(result.cookies['sessionid']['httponly'])
        self.assertEqual(int(result.cookies['sessionid']['max-age']),2592000)
        self.assertEqual(self.client.get('/api/me/').status_code,200)
        sessions=self.client.get('/api/account/sessions/').data
        self.assertEqual(len(sessions),1)
        self.assertTrue(sessions[0]['current'])
        self.assertNotIn('session_key',sessions[0])
        self.assertEqual(Token.objects.count(),0)
    def test_session_profile_write_needs_csrf(self):
        self.assertEqual(self.sign_in().status_code,200)
        self.assertEqual(self.client.put('/api/account/',{'display_name':'Ada'},format='json').status_code,403)
        self.assertEqual(self.client.put('/api/account/',{'display_name':'Ada'},format='json',**self.csrf()).status_code,200)
        self.assertEqual(self.client.get('/api/me/').data['display_name'],'Ada')
        self.assertEqual(self.client.post('/api/auth/session/logout/',{},format='json',**self.csrf()).status_code,204)
        self.assertEqual(self.client.get('/api/me/').status_code,401)
    def test_register_validates_and_prevents_duplicate_email(self):
        data={'username':'new-builder','email':'NEW@example.com','password':self.password,'display_name':'Learner'}
        response=self.client.post('/api/auth/session/register/',data,format='json',**self.csrf())
        self.assertEqual(response.status_code,201,response.data)
        self.assertEqual(self.client.get('/api/account/').data['display_name'],'Learner')
        self.assertEqual(response.cookies['sessionid']['max-age'],'')
        self.client.post('/api/auth/session/logout/',{},format='json',**self.csrf())
        data['username']='different';data['email']='new@EXAMPLE.com'
        self.assertEqual(self.client.post('/api/auth/session/register/',data,format='json',**self.csrf()).status_code,400)
        data['email']='other@example.com';data['password']='password'
        self.assertEqual(self.client.post('/api/auth/session/register/',data,format='json',**self.csrf()).status_code,400)
    def test_ambiguous_legacy_email_cannot_choose_an_account(self):
        User.objects.create_user('legacy',email='builder@example.com',password=self.password)
        self.assertEqual(self.sign_in(username='builder@example.com').status_code,400)
        self.assertEqual(self.sign_in().status_code,200)
    def test_password_change_preserves_current_revokes_other_and_token(self):
        second=APIClient(enforce_csrf_checks=True)
        self.assertEqual(self.sign_in(second).status_code,200)
        self.assertEqual(self.sign_in().status_code,200)
        Token.objects.create(user=self.user)
        route='/api/account/password/'
        body={'current_password':'wrong','password':'Replacement-password-8372!'}
        self.assertEqual(self.client.post(route,body,format='json',**self.csrf()).status_code,400)
        body['current_password']=self.password
        response=self.client.post(route,body,format='json',**self.csrf())
        self.assertEqual(response.status_code,200,response.data)
        self.assertEqual(self.client.get('/api/me/').status_code,200)
        self.assertEqual(second.get('/api/me/').status_code,401)
        self.assertEqual(AccountSession.objects.count(),1)
        self.assertEqual(Token.objects.count(),0)
        self.assertEqual(self.client.get('/api/account/sessions/').data[0]['current'],True)
    def test_device_revocation_and_ownership(self):
        second=APIClient(enforce_csrf_checks=True);self.sign_in(second);self.sign_in()
        rows=self.client.get('/api/account/sessions/').data
        other=next(row for row in rows if not row['current'])
        current=next(row for row in rows if row['current'])
        self.assertEqual(self.client.delete(f"/api/account/sessions/{current['id']}/",**self.csrf()).status_code,400)
        self.assertEqual(self.client.delete(f"/api/account/sessions/{other['id']}/",**self.csrf()).status_code,204)
        self.assertEqual(second.get('/api/me/').status_code,401)
        self.assertEqual(self.client.delete(f"/api/account/sessions/{other['id']}/",**self.csrf()).status_code,404)

class WorkspaceDiscoveryTests(APITestCase):
    def setUp(self):
        self.user=User.objects.create_user('learner')
        self.other=User.objects.create_user('other')
        self.program=Program.objects.create(slug='path',title='Path',category='Cohort',duration='8 weeks')
        self.lesson=Lesson.objects.create(program=self.program,order=1,title='Model budgets',module='Foundations',content='Measure latency and cost before deploying.',task='Measure')
        self.hidden=Program.objects.create(slug='hidden',title='Hidden',category='Engineering')
        Lesson.objects.create(program=self.hidden,order=1,title='Model budgets hidden',module='Secret',content='Hidden')
        Enrollment.objects.create(user=self.user,program=self.program)
        LessonNote.objects.create(user=self.other,lesson=self.lesson,text='Secret-other-only')
        LessonNote.objects.create(user=self.user,lesson=self.lesson,text='My personal-mnemonic for context')
        self.client.force_authenticate(self.user)
    def test_search_enrollment_and_notes_are_private(self):
        self.assertEqual(len(self.client.get('/api/search/?q=budgets').data),1)
        result=self.client.get('/api/search/?q=personal-mnemonic').data
        self.assertEqual(result[0]['match'],'Private note')
        self.assertEqual(self.client.get('/api/search/?q=Secret-other-only').data,[])
        self.assertEqual(self.client.get('/api/search/?q=a').status_code,400)
    def test_bookmarks_are_private_idempotent_and_require_enrollment(self):
        url=f'/api/lessons/{self.lesson.pk}/bookmark/'
        self.assertEqual(len(self.client.post(url).data),1)
        self.assertEqual(len(self.client.post(url).data),1)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get('/api/bookmarks/').data,[])
        self.assertEqual(self.client.post(url).status_code,403)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(url).data,[])
    def test_portfolio_never_returns_another_students_work(self):
        ProjectSubmission.objects.create(user=self.user,lesson=self.lesson,artifact_url='https://example.com/mine',evidence='My work',measurements={})
        ProjectSubmission.objects.create(user=self.other,lesson=self.lesson,artifact_url='https://example.com/private',evidence='Private work',measurements={})
        result=self.client.get('/api/portfolio/').data
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['evidence'],'My work')
