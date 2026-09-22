from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.contrib.auth.models import User
from django.contrib.auth import login

from .models import Assignment
from .forms import AssignmentForm

def home(request):
    assignments = (
        Assignment.objects.filter(owner=request.user)
        if request.user.is_authenticated else Assignment.objects.none()
    )

    return render(request, 'home.html', {
        'assignments': assignments
    })

@login_required(login_url='login')
def assignment(request):
    form = AssignmentForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        new_assignment = form.save(commit=False)
        new_assignment.owner = request.user
        new_assignment.save()
        return redirect('home')
    return render(request, 'assignment.html', {'form': form})

@login_required(login_url='login')
@require_POST
def complete_assignment(request, id):

    assignment = get_object_or_404(Assignment, id=id, owner=request.user)

    assignment.completed = True
    assignment.save()

    return redirect('home')

@login_required(login_url='login')
@require_POST
def delete_assignment(request, id):

    assignment = get_object_or_404(Assignment, id=id, owner=request.user)

    assignment.delete()

    return redirect('home')

@login_required(login_url='login')
def edit_assignment(request, id):
    assignment = get_object_or_404(Assignment, id=id, owner=request.user)
    form = AssignmentForm(
        request.POST if request.method == 'POST' else None, instance=assignment
    )
    if request.method == 'POST' and form.is_valid():
        if {'due_date', 'due_time', 'reminder'} & set(form.changed_data):
            form.instance.reminder_sent_at = None
        form.save()
        return redirect('home')
    return render(request, 'edit_assignment.html', {
        'assignment': assignment,
        'form': form,
    })

def signup(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not all([username, email, password, confirm_password]):
            return render(request, 'signup.html', {
                'error': 'Please fill in all fields.'
            })

        if password != confirm_password:
            return render(request, 'signup.html', {
                'error': 'Passwords do not match.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {
                'error': 'That username is already taken.'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect('home')

    return render(request, 'signup.html')
