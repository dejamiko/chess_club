"""Tests of the log out view"""
from django.test import TestCase
from clubs.models import User
from django.urls import reverse
from .helpers import LogInTester

class LogOutViewTestCase(TestCase, LogInTester):
    """Tests of the log out view"""

    def setUp(self):
        self.url = reverse('log_out')
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

    def test_redirect(self):
        #Test redirect behaviour for logged in and logged out users
        pass

    def test_log_out_url(self):
        self.assertEqual(self.url, '/home/log_out/')

    def test_get_log_out(self):
        self.client.login(username='@johndoe', password='#NDGDR98adada123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url, status_code=302, target_status_code = 200)
        template_dict = { 'log_in.html', 'base_content.html', 'base.html', 'partials/navbar.html' }
        for t in template_dict:
            self.assertTemplateUsed(response, t)
        self.assertFalse(self._is_logged_in())
