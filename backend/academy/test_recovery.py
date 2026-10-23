import re
import smtplib
from datetime import datetime, timedelta
from io import StringIO
from unittest.mock import patch
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.management import call_command, CommandError
from django.test import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from .models import AccountSession


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', EMAIL_HOST='smtp.example.com', ACADEMY_PUBLIC_URL='https://academy.example.com', PASSWORD_RESET_TIMEOUT=3600)
class RecoveryDeliveryTests(APITestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.user = User.objects.create_user('mail-learner', email='learner@example.com', password='Original-course-pass-3847!')
        self.route = '/api/auth/password-reset/'

    def request_reset(self):
        response = self.client.post(self.route, {'email': self.user.email}, format='json')
        self.assertEqual(response.status_code, 200)
        return re.search(r'/#/reset/([^/]+)/([^\s]+)', mail.outbox[-1].body).groups()

    def test_html_plain_text_canonical_origin_and_expiry_copy(self):
        self.request_reset()
        message = mail.outbox[0]
        self.assertIn('https://academy.example.com/#/reset/', message.body)
        self.assertIn('60 minutes', message.body)
        self.assertEqual(message.alternatives[0].mimetype, 'text/html')
        self.assertIn('Choose a new password', message.alternatives[0].content)
        self.assertNotIn('testserver', message.body)

    def test_expired_link_and_weak_password_do_not_change_password(self):
        now = datetime(2026, 10, 23, 8)
        with patch.object(default_token_generator, '_now', return_value=now):
            uid, token = self.request_reset()
            response = self.client.post(self.route+'confirm/', {'uid':uid,'token':token,'password':'password'}, format='json')
            self.assertEqual(response.status_code, 400)
        with patch.object(default_token_generator, '_now', return_value=now+timedelta(seconds=3601)):
            response = self.client.post(self.route+'confirm/', {'uid':uid,'token':token,'password':'Replacement-course-pass-8357!'}, format='json')
            self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Original-course-pass-3847!'))

    def test_reset_revokes_browser_sessions_and_tokens(self):
        signed_in = APIClient()
        signed_in.login(username=self.user.username, password='Original-course-pass-3847!')
        AccountSession.objects.create(user=self.user, session_key=signed_in.session.session_key, device='Synthetic browser')
        Token.objects.create(user=self.user)
        uid, token = self.request_reset()
        response = self.client.post(self.route+'confirm/', {'uid':uid,'token':token,'password':'Replacement-course-pass-8357!'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(signed_in.get('/api/me/').status_code, 401)
        self.assertFalse(AccountSession.objects.filter(user=self.user).exists())
        self.assertFalse(Token.objects.filter(user=self.user).exists())
        self.assertEqual(self.client.post(self.route+'confirm/', {'uid':uid,'token':token,'password':'Another-course-pass-8357!'}, format='json').status_code, 400)

    def test_delivery_failure_is_observable_without_account_or_secret_disclosure(self):
        with patch('academy.recovery.EmailMultiAlternatives.send', side_effect=smtplib.SMTPAuthenticationError(535,b'synthetic-secret')):
            with self.assertLogs('academy.experience', level='WARNING') as captured:
                result = self.client.post(self.route, {'email':self.user.email}, format='json')
        missing = self.client.post(self.route, {'email':'missing@example.com'}, format='json')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, missing.data)
        self.assertNotIn('synthetic-secret', str(captured.output))
        self.assertNotIn(self.user.email, str(captured.output))

    def test_check_command_authenticates_without_sending_by_default(self):
        with patch('academy.management.commands.check_email.get_connection') as connect:
            output = StringIO()
            call_command('check_email', stdout=output)
            connect.assert_called_once_with(fail_silently=False)
        self.assertIn('succeeded', output.getvalue())

    @override_settings(EMAIL_USE_TLS=True, EMAIL_USE_SSL=True)
    def test_check_command_rejects_conflicting_encryption(self):
        with self.assertRaises(CommandError):
            call_command('check_email')

    def test_check_command_auth_error_is_sanitized(self):
        with patch('academy.management.commands.check_email.get_connection', side_effect=smtplib.SMTPAuthenticationError(535,b'synthetic-secret')):
            with self.assertRaises(CommandError) as error:
                call_command('check_email')
        self.assertNotIn('synthetic-secret', str(error.exception))
