"""Tests of the sign up view"""
from django.test import TestCase
from clubs.forms import SignUpForm
from django.urls import reverse
from clubs.models import User
from django.contrib.auth.hashers import check_password
from .helpers import LogInTester


class SignUpViewTestCase(TestCase, LogInTester):
    """Tests of the sign up view"""

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'username': '@janedoe',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@example.org',
            'bio': 'My bio',
            'chess_exp': 'Beginner',
            'personal_statement': 'Jane doe personal statement',
            'new_password': '#NDGDR98adada123',
            'password_confirmation': '#NDGDR98adada123'
        }

    def test_sign_up_url(self):
        self.assertEqual(self.url, '/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_sign_up(self):
        self.form_input['username'] = ''
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_succesful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('home_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        template_dict = {'home_page.html', 'base_content.html', 'base.html', 'partials/navbar.html'}
        for t in template_dict:
            self.assertTemplateUsed(response, t)
        user = User.objects.get(username='@janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        self.assertEqual(user.bio, 'My bio')
        self.assertEqual(user.chess_exp, 'Beginner')
        self.assertEqual(user.personal_statement, 'Jane doe personal statement')
        is_password_correct = check_password('#NDGDR98adada123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())
