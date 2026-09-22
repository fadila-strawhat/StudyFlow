from datetime import datetime, timedelta

# Create your models here.
from django.db import models
from django.conf import settings


class Assignment(models.Model):
    # Older assignments have no known owner and remain hidden from user accounts.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='assignments', null=True, blank=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    due_time = models.TimeField()

    PRIORITY_CHOICES = [
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ]
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='medium')

    REMINDER_CHOICES = [
        ('none', 'No reminder'),
        ('1_hour', '1 hour before'),
        ('1_day', '1 day before'),
        ('2_days', '2 days before'),
        ('3_days', '3 days before'),
    ]

    reminder = models.CharField(
        max_length=10,
        choices=REMINDER_CHOICES,
        default='1_hour'
    )
    completed = models.BooleanField(default=False)
    def __str__(self):
        return self.title

def get_reminder_time(self):
        due_datetime = datetime.combine(
            self.due_date,
            self.due_time
        )

        if self.reminder == '1_hour':
            return due_datetime - timedelta(hours=1)

        elif self.reminder == '1_day':
            return due_datetime - timedelta(days=1)

        elif self.reminder == '2_days':
            return due_datetime - timedelta(days=2)

        elif self.reminder == '3_days':
            return due_datetime - timedelta(days=3)

        return None
