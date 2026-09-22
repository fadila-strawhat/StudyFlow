from django import forms

from .models import Assignment


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'due_time', 'priority', 'reminder']
        labels = {'title': 'Assignment Title', 'due_date': 'Due Date', 'due_time': 'Due Time'}
        widgets = {
            'due_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'due_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }
