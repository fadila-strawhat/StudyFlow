from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from app.models import Assignment


class Command(BaseCommand):
    help = 'Send unsent reminders for unfinished assignments before their deadline.'

    def handle(self, *args, **options):
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            raise CommandError('Configure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD.')
        now = timezone.now()
        candidates = Assignment.objects.filter(
            completed=False, reminder_sent_at__isnull=True, owner__isnull=False,
            owner__is_active=True, due_date__gte=timezone.localdate(),
        ).exclude(reminder='none').exclude(owner__email='')
        sent = failed = 0
        for pk in candidates.values_list('pk', flat=True).iterator():
            try:
                with transaction.atomic():
                    assignment = Assignment.objects.select_for_update().get(pk=pk)
                    reminder_at = assignment.get_reminder_time()
                    if (assignment.completed or assignment.reminder_sent_at or
                            reminder_at is None or
                            not reminder_at <= now < assignment.get_due_datetime()):
                        continue
                    owner = assignment.owner
                    if not owner or not owner.is_active or not owner.email:
                        continue
                    due = assignment.get_due_datetime().strftime('%d %b %Y at %H:%M %Z')
                    count = send_mail(
                        'StudyFlow assignment reminder',
                        f'Hi {owner.username},\n\nYour assignment "{assignment.title}" '
                        f'is due on {due}.\n\nTo stop this reminder, choose '
                        '"No reminder" when editing the assignment.\n\nStudyFlow',
                        settings.DEFAULT_FROM_EMAIL, [owner.email],
                    )
                    if count != 1:
                        raise RuntimeError('Email not accepted')
                    assignment.reminder_sent_at = now
                    assignment.save(update_fields=['reminder_sent_at'])
                    sent += 1
            except Exception:
                # Do not expose recipient addresses, credentials, or SMTP replies in logs.
                failed += 1
                self.stderr.write(f'Reminder delivery failed for assignment {pk}.')
        self.stdout.write(f'Sent {sent} reminder(s); failed {failed}.')
        if failed:
            raise CommandError('Some reminders failed; they will retry on the next run.')
