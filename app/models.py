from datetime import datetime, timedelta

# Create your models here.
from django.db import models


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    due_time = models.TimeField()

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
