from datetime import time

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Assignment


class AuthenticationTests(TestCase):
    def setUp(self):
        self.credentials = {'username': 'student', 'password': 'StudyFlow-test-482!'}

    def test_signup_logs_in_and_opens_home(self):
        response = self.client.post(reverse('signup'), {
            **self.credentials,
            'email': 'student@example.com',
            'confirm_password': self.credentials['password'],
        })
        self.assertRedirects(response, reverse('home'))
        user = User.objects.get(username='student')
        self.assertTrue(user.check_password(self.credentials['password']))
        self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))

    def test_signup_links_to_login(self):
        response = self.client.get(reverse('signup'))
        self.assertContains(response, f'href="{reverse("login")}"')
        self.assertNotContains(response, 'coming soon')

    def test_login_opens_home(self):
        user = User.objects.create_user(**self.credentials)
        response = self.client.post(reverse('login'), self.credentials)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))

    def test_invalid_login_shows_error_without_signing_in(self):
        User.objects.create_user(**self.credentials)
        response = self.client.post(reverse('login'), {
            **self.credentials, 'password': 'wrong-password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].non_field_errors())
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_invalid_signup_does_not_create_account(self):
        for extra in [{'confirm_password': 'mismatch'}, {'username': ''}]:
            with self.subTest(extra=extra):
                response = self.client.post(reverse('signup'), {
                    **self.credentials, 'email': 'student@example.com',
                    'confirm_password': self.credentials['password'], **extra,
                })
                self.assertEqual(response.status_code, 200)
                self.assertIn('error', response.context)
                self.assertFalse(User.objects.exists())


class AssignmentPrivacyTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner')
        self.other = User.objects.create_user(username='other')
        self.assignment = Assignment.objects.create(
            owner=self.owner, title='Private report', description='Private notes',
            due_date='2026-10-15', due_time='09:00',
        )

    def test_home_only_shows_current_users_assignments(self):
        Assignment.objects.create(title='Legacy report', description='Old notes',
                                  due_date='2026-10-15', due_time='09:00')
        for user in [self.owner, self.other, None]:
            with self.subTest(user=user):
                self.client.logout()
                if user:
                    self.client.force_login(user)
                response = self.client.get(reverse('home'))
                self.assertEqual(list(response.context['assignments']),
                                 [self.assignment] if user == self.owner else [])
                self.assertNotContains(response, 'Legacy report')

    def test_other_user_cannot_access_or_change_assignment(self):
        self.client.force_login(self.other)
        for route in ['edit_assignment', 'complete_assignment', 'delete_assignment']:
            url = reverse(route, args=[self.assignment.pk])
            self.assertEqual(self.client.post(url, {'title': 'Changed'}).status_code, 404)
        self.assertEqual(self.client.get(reverse('edit_assignment', args=[self.assignment.pk])).status_code, 404)
        self.assignment.refresh_from_db()
        self.assertFalse(self.assignment.completed)
        self.assertEqual(self.assignment.title, 'Private report')

    def test_guests_must_log_in_to_manage_assignments(self):
        urls = [reverse('add_assignment')] + [
            reverse(route, args=[self.assignment.pk])
            for route in ['edit_assignment', 'complete_assignment', 'delete_assignment']
        ]
        for url in urls:
            self.assertRedirects(self.client.post(url), f'{reverse("login")}?next={url}')
        self.assertEqual(Assignment.objects.count(), 1)

    def test_owner_can_complete_and_delete_only_by_post(self):
        self.client.force_login(self.owner)
        for route in ['complete_assignment', 'delete_assignment']:
            url = reverse(route, args=[self.assignment.pk])
            self.assertEqual(self.client.get(url).status_code, 405)
            self.assertRedirects(self.client.post(url), reverse('home'))
            if route == 'complete_assignment':
                self.assignment.refresh_from_db()
                self.assertTrue(self.assignment.completed)
        self.assertFalse(Assignment.objects.exists())

    def test_navbar_and_logout(self):
        for route in ['home', 'signup', 'login']:
            response = self.client.get(reverse(route))
            self.assertContains(response, f'href="{reverse("signup")}"')
            self.assertContains(response, f'href="{reverse("login")}"')
        self.client.force_login(self.owner)
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'owner')
        self.assertContains(response, f'action="{reverse("logout")}"')
        self.assertRedirects(self.client.post(reverse('logout')), reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)


class AssignmentFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner')
        self.client.force_login(self.user)
        self.data = {
            'title': 'Database report',
            'description': 'Normalize the database.',
            'due_date': '2026-10-15',
            'due_time': '23:59',
            'priority': 'high',
            'reminder': '1_day',
        }

    def test_create_saves_time_and_displays_priority(self):
        response = self.client.post(reverse('add_assignment'), self.data)
        self.assertRedirects(response, reverse('home'))
        assignment = Assignment.objects.get()
        self.assertEqual(assignment.owner, self.user)
        self.assertEqual(assignment.due_time, time(23, 59))
        self.assertEqual(assignment.priority, 'high')
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'High Priority')
        self.assertContains(response, 'priority-high')
        self.assertContains(response, '11:59 p.m.')

    def test_edit_preserves_and_updates_time_and_priority(self):
        assignment = Assignment.objects.create(owner=self.user, **self.data)
        url = reverse('edit_assignment', args=[assignment.pk])
        response = self.client.get(url)
        self.assertContains(response, 'value="23:59"')
        self.assertContains(response, 'value="high" selected')
        for priority in ['low', 'medium']:
            with self.subTest(priority=priority):
                response = self.client.post(url, {**self.data, 'due_time': '09:30', 'priority': priority})
                self.assertRedirects(response, reverse('home'))
                assignment.refresh_from_db()
                self.assertEqual(assignment.due_time, time(9, 30))
                self.assertEqual(assignment.priority, priority)
                self.assertContains(self.client.get(reverse('home')), f'priority-{priority}')

    def test_invalid_values_do_not_save_and_keep_entered_title(self):
        for field, value in [('priority', 'urgent'), ('due_time', '25:99')]:
            with self.subTest(field=field):
                response = self.client.post(reverse('add_assignment'), {**self.data, field: value})
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context['form'].errors)
                self.assertContains(response, 'Database report')
                self.assertFalse(Assignment.objects.exists())
