"""Tests of the log in view"""
from django.test import TestCase
from clubs.models import User
from django.urls import reverse
from clubs.tests.views.helpers import reverse_with_next
from .helpers import LogInTester


class EditProfileTestCase(TestCase, LogInTester):
    """Tests of the edit profile view"""
    fixtures = ["clubs/tests/fixtures/default_user.json"]

    def setUp(self):
        self.url = reverse('profile')
        self.login_url = reverse('log_in')
        self.user = User.objects.get(email="johndoe@example.com")

    def test_logged_in_redirect(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_profile_url(self):
        self.assertEqual(self.url, '/home/profile/')

    def test_profile_is_correct(self):
        self.client.login(email=self.user.email, password='Password123')
        curr_profile = self.client.get(self.url)
        profile_user = curr_profile.context["user"]
        self.assertEqual(self.user.first_name, profile_user.first_name)
        self.assertEqual(self.user.last_name, profile_user.last_name)
        self.assertEqual(self.user.email, profile_user.email)
        self.assertEqual(self.user.bio, profile_user.bio)
        self.assertEqual(self.user.chess_exp, profile_user.chess_exp)
        self.assertEqual(self.user.personal_statement, profile_user.personal_statement)
