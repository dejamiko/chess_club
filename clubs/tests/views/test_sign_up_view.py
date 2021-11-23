"""Tests of the sign up view"""
from django.test import TestCase
from clubs.forms import SignUpForm
from django.urls import reverse
from clubs.models import User
from django.contrib.auth.hashers import check_password
from .helpers import LogInTester

class SignUpViewTestCase(TestCase, LogInTester):
    """Tests of the sign up view"""

    fixtures = ["clubs/tests/fixtures/default_user.json"]

    def setUp(self):
        self.url = reverse('sign_up')

        self.user = User.objects.get(email="johndoe@example.com")
        self.form_input = {
        'username': self.user.username,
        'first_name': self.user.first_name,
        'last_name': self.user.last_name,
        'email': self.user.email,
        'bio': self.user.bio,
        'chess_exp' : self.user.chess_exp,
        'personal_statement' : self.user.personal_statement,
        'new_password': self.user.password,
        'password_confirmation' : self.user.password
        }

    def test_redirect(self):
        #Test redirect behaviour for logged in and logged out users
        pass

    def test_sign_up_url(self):
        self.assertEqual(self.url, '/sign_up/')

    def test_get_sign_up(self):
        response=self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form,SignUpForm))
        self.assertFalse(form.is_bound)

    def test_get_sign_up_redirect_when_logged_in(self):
        self.client.login(username=self.user.username, password='#NDGDR98adada123')
        response=self.client.get(self.url, follow=True)
        redirect_url=reverse('home_page')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code = 200)
        self.assertTemplateUsed(response, 'home_page.html')

    def test_unsuccesful_sign_up(self):
        self.form_input['username'] = ''
        before_count = User.objects.count()
        response=self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response .status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form,SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_succesful_sign_up(self):
        before_count = User.objects.count()
        response=self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('home_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        template_dict = { 'home_page.html', 'base_content.html', 'base.html', 'partials/navbar.html' }
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
    #
    # def test_post_log_in_redirect_when_logged_in(self):
    #     self.client.login(username=self.user.username, password=self.user.password)
    #     before_count = User.objects.count()
    #     response=self.client.post(self.url, self.form_input, follow=True)
    #     after_count = User.objects.count()
    #     self.assertEqual(after_count, before_count)
    #     redirect_url=reverse('home_page')
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code = 200)
    #     self.assertTemplateUsed(response, 'home_page.html')
