"""Tests of the log in view"""
from django.test import TestCase
from clubs.forms import LogInForm, EditForm
from clubs.models import User
from django.urls import reverse
from clubs.tests.views.helpers import reverse_with_next
from .helpers import LogInTester


class EditProfileTestCase(TestCase, LogInTester):
    """Tests of the edit profile view"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('edit_profile')
        self.login_url = reverse('log_in')
        self.user = User.objects.get(email="johndoe@example.com")
        self.edit_profile_form_input =  { 'username': '@NOTjohndoe' , 'first_name' : 'NOTJohn',
        'last_name': 'NOTdoe', 'email' : 'NOTjohndoe@test.com', 'bio' : 'NOT my bio',
        'chess_exp' : 'Advanced', 'personal_statement' :'NOT john doe personal statement'
        }

    def test_logged_in_redirect(self):
        redirect_url=reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_profile_url(self):
        self.assertEqual(self.url, '/home/profile/edit/')

    def test_unsuccessful_profile_update_due_to_duplicate_username(self):
        self.client.login(username=self.user.username, password='Password123')
        self.edit_profile_form_input['username'] = 'janedoe'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.edit_profile_form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email,'johndoe@example.com')
        self.assertEqual(self.user.bio,"Hi, I'm John Doe" )
        self.assertEqual(self.user.chess_exp, 'Beginner')
        self.assertEqual(self.user.personal_statement, "I've started playing chess after I've watched the Queen's Gambit on Netflix. Such a cool game!")

    def test_edit_profile_changes_attributes(self):
        self.client.login(username=self.user.username, password='Password123')

        response = self.client.post(self.url, self.edit_profile_form_input, follow=True)
        response_url = reverse('profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, '@NOTjohndoe')
        self.assertEqual(self.user.first_name, 'NOTJohn')
        self.assertEqual(self.user.last_name, 'NOTdoe')
        self.assertEqual(self.user.email,'NOTjohndoe@test.com')
        self.assertEqual(self.user.bio,'NOT my bio' )
        self.assertEqual(self.user.chess_exp, 'Advanced')
        self.assertEqual(self.user.personal_statement, 'NOT john doe personal statement')

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.edit_profile_form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
