"""Check SMTP connectivity/authentication without printing secrets."""
import smtplib
from urllib.parse import urlsplit
from email.utils import parseaddr
from django.conf import settings
from django.core.mail import get_connection, send_mail
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = 'Validate recovery settings and authenticate SMTP. Optionally send a diagnostic email.'

    def add_arguments(self, parser):
        parser.add_argument('--recipient', help='Send one diagnostic to an address you control.')

    def handle(self, *args, **options):
        if not settings.EMAIL_HOST:
            raise CommandError('Set EMAIL_HOST before enabling recovery delivery.')
        origin = urlsplit(settings.ACADEMY_PUBLIC_URL)
        if origin.scheme not in ('http', 'https') or not origin.hostname or origin.path or origin.query or origin.fragment or origin.username:
            raise CommandError('ACADEMY_PUBLIC_URL must be an HTTP(S) origin with no path or credentials.')
        if settings.EMAIL_USE_TLS and settings.EMAIL_USE_SSL:
            raise CommandError('Choose STARTTLS or implicit SSL, not both.')
        if not 1 <= settings.EMAIL_PORT <= 65535 or not 0 < settings.EMAIL_TIMEOUT <= 60:
            raise CommandError('Use a valid SMTP port and a timeout between 1 and 60 seconds.')
        if settings.PASSWORD_RESET_TIMEOUT < 60:
            raise CommandError('PASSWORD_RESET_TIMEOUT must be at least 60 seconds.')
        try:
            validate_email(parseaddr(settings.DEFAULT_FROM_EMAIL)[1])
            if options['recipient']:
                validate_email(options['recipient'])
        except ValidationError:
            raise CommandError('Set a valid verified sender and optional recipient address.') from None
        try:
            with get_connection(fail_silently=False) as connection:
                self.stdout.write(self.style.SUCCESS('SMTP connection and configured authentication succeeded.'))
                if options['recipient']:
                    count = send_mail('Practical AI — SMTP delivery check',
                                      'The academy SMTP configuration accepted this diagnostic. Check receipt and spam placement; SMTP acceptance alone does not prove inbox delivery.',
                                      settings.DEFAULT_FROM_EMAIL, [options['recipient']], connection=connection, fail_silently=False)
                    if count != 1:
                        raise CommandError('SMTP did not accept the diagnostic email.')
                    self.stdout.write(self.style.SUCCESS('One diagnostic accepted by SMTP. Confirm receipt in the recipient inbox.'))
        except smtplib.SMTPAuthenticationError:
            raise CommandError('SMTP authentication failed. Check the username and provider app password.') from None
        except (smtplib.SMTPException, OSError, ValueError):
            raise CommandError('SMTP connection or delivery failed. Check host, port, TLS mode, sender verification and network access; no secrets were logged.') from None
        self.stdout.write('Reset links use the configured ACADEMY_PUBLIC_URL; recovery tokens are not printed.')
