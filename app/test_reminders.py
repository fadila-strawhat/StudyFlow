from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command, CommandError
from django.test import TestCase, override_settings
from django.utils import timezone
from app.models import Assignment


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   EMAIL_HOST_USER='sender@example.com', EMAIL_HOST_PASSWORD='test')
class ReminderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('student', email='student@example.com')
        self.now = timezone.now()
        due = timezone.localtime(self.now + timedelta(minutes=30))
        self.assignment = Assignment.objects.create(
            owner=self.user, title='Report', description='Notes', due_date=due.date(),
            due_time=due.time().replace(tzinfo=None), reminder='1_hour',
        )

    def run_job(self):
        call_command('send_reminders', stdout=StringIO(), stderr=StringIO())

    def test_sends_to_owner_only_once(self):
        self.run_job()
        self.run_job()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assignment.refresh_from_db()
        self.assertIsNotNone(self.assignment.reminder_sent_at)

    def test_skips_completed_disabled_future_and_overdue(self):
        for changes in [{'completed': True}, {'reminder': 'none'},
                        {'due_date': timezone.localdate() + timedelta(days=5)},
                        {'due_date': timezone.localdate() - timedelta(days=1)}]:
            with self.subTest(changes=changes):
                with transaction_for_test(self.assignment, changes):
                    self.run_job()
        self.assertEqual(len(mail.outbox), 0)

    def test_delivery_failure_can_retry(self):
        with patch('app.management.commands.send_reminders.send_mail', side_effect=OSError):
            with self.assertRaises(CommandError):
                self.run_job()
        self.assignment.refresh_from_db()
        self.assertIsNone(self.assignment.reminder_sent_at)
        self.run_job()
        self.assertEqual(len(mail.outbox), 1)


from contextlib import contextmanager


@contextmanager
def transaction_for_test(assignment, changes):
    original = {key: getattr(assignment, key) for key in changes}
    Assignment.objects.filter(pk=assignment.pk).update(**changes)
    try:
        yield
    finally:
        Assignment.objects.filter(pk=assignment.pk).update(**original)
