"""Tests of the log in view"""
from django.contrib import messages
from django.test import TestCase
from clubs.forms import LogInForm
from clubs.models import User
from django.urls import reverse
from .helpers import LogInTester, reverse_with_next


class LogInViewTestCase(TestCase, LogInTester):
    """Tests of the log in view"""
    fixtures = ["clubs/tests/fixtures/default_user.json"]

    def setUp(self):
        self.url = reverse("log_in")
        self.user = User.objects.get(email="johndoe@example.com")

    def test_redirect(self):
        #Test redirect behaviour for logged in and logged out users
        pass

    def test_log_in_url(self):
        self.assertEqual(self.url, '/log_in/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form,LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(next)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_get_log_in_with_redirect(self):
        destination_url=reverse('users')
        self.url = reverse_with_next('log_in', destination_url)
        response=self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form,LogInForm))
        self.assertFalse(form.is_bound)
        self.assertEqual(next, destination_url)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_get_log_in_redirect_when_logged_in(self):
        self.client.login(username=self.user.username, password='Password123')
        response=self.client.get(self.url, follow=True)
        redirect_url=reverse('home_page')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code = 200)
        self.assertTemplateUsed(response, 'home_page.html')

    def test_unsuccesful_log_in(self):
        form_input = { 'username': '@johndoe22', 'password': 'xy' + 'Password123' }
        response=self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_succesful_log_in(self):
        form_input = { 'username': self.user.username, 'password': 'Password123' }
        response=self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('home_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        template_dict = {'home_page.html', 'base_content.html', 'base.html', 'partials/navbar.html'}
        for t in template_dict:
            self.assertTemplateUsed(response, t)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_succesful_log_in_with_redirect(self):
        redirect_url=reverse('home_page')
        form_input = { 'username': self.user.username , 'password': 'Password123', 'next':redirect_url }
        response=self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code = 200)
        template_dict = {'user_list.html', 'base_content.html', 'base.html', 'partials/navbar.html'}

    def test_post_log_in_redirect_when_logged_in(self):
        self.client.login(username=self.user.username, password='Password123')
        form_input = { 'username': self.user.username, 'password': 'Password123'}
        response=self.client.post(self.url, form_input, follow=True)
        redirect_url=reverse('home_page')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code = 200)
        self.assertTemplateUsed(response, 'home_page.html')

    def test_valid_log_in_by_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form_input = { 'username': self.user.username, 'password': 'Password123' }
        response=self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
