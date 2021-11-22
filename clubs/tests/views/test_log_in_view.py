"""Tests of the log in view"""
from django.contrib import messages
from django.test import TestCase
from clubs.forms import LogInForm
from clubs.models import User
from django.urls import reverse
from .helpers import LogInTester


class LogInViewTestCase(TestCase, LogInTester):
    """Tests of the log in view"""

    def setUp(self):
        self.url = reverse('log_in')
        self.user = User.objects.create_user(
            username="@johndoe",
            first_name="john",
            last_name="doe",
            email="johndoe@test.com",
            bio='My bio',
            password='#NDGDR98adada123',
            chess_exp="Beginner",
            personal_statement='john doe personal statement',
        )

    def test_log_in_url(self):
        self.assertEqual(self.url, '/log_in/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_log_in(self):
        form_input = {'username': '@johndoe', 'password': 'xy' + '#NDGDR98adada123'}
        response = self.client.post(self.url, form_input)
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
        form_input = {'username': '@johndoe', 'password': '#NDGDR98adada123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('home_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        template_dict = {'home_page.html', 'base_content.html', 'base.html', 'partials/navbar.html'}
        for t in template_dict:
            self.assertTemplateUsed(response, t)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_valid_log_in_by_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form_input = {'username': '@johndoe', 'password': '#NDGDR98adada123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
