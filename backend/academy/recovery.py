"""Recovery delivery with observable failures and no credential/token logging."""
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class RecoveryForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):
        # Django's default form catches delivery exceptions internally. Surface
        # them to our endpoint so it can log a sanitized operational failure.
        context = {**context, 'expiry_minutes': settings.PASSWORD_RESET_TIMEOUT // 60}
        subject = ''.join(render_to_string(subject_template_name, context).splitlines())
        body = render_to_string(email_template_name, context)
        message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name:
            message.attach_alternative(render_to_string(html_email_template_name, context), 'text/html')
        if message.send(fail_silently=False) != 1:
            raise OSError('SMTP did not accept the recovery message.')
