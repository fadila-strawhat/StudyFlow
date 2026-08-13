from django.shortcuts import render,redirect

from django.contrib.auth.models import User

from .models import Assignment

def home(request):
    assignments = Assignment.objects.all()

    return render(request, 'home.html', {
        'assignments': assignments
    })

def assignment(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        due_date = request.POST['due_date']
        due_time = request.POST['due_time']
        reminder = request.POST['reminder']
    
        Assignment.objects.create(
            title=title,
            description=description,
            due_date=due_date,
            due_time=due_time,
            reminder=reminder
        )
        return redirect('home')
    return render(request, 'assignment.html')

def complete_assignment(request, id):

    assignment = Assignment.objects.get(id=id)

    assignment.completed = True
    assignment.save()

    return redirect('home')

def delete_assignment(request, id):

    assignment = Assignment.objects.get(id=id)

    assignment.delete()

    return redirect('home')

def edit_assignment(request, id):

    assignment = Assignment.objects.get(id=id)

    if request.method == 'POST':

        assignment.title = request.POST['title']
        assignment.description = request.POST['description']
        assignment.due_date = request.POST['due_date']
        assignment.due_time = request.POST['due_time']
        assignment.reminder = request.POST['reminder']

        assignment.save()

        return redirect('home')

    return render(request, 'edit_assignment.html', {
        'assignment': assignment
    })

def signup(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'signup.html', {
                'error': 'Passwords do not match.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {
                'error': 'That username is already taken.'
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('signup')

    return render(request, 'signup.html')