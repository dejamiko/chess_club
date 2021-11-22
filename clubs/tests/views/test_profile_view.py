"""Tests of the log in view"""
from django.contrib import messages
from django.test import TestCase
from clubs.forms import LogInForm
from clubs.models import User
from django.urls import reverse
from .helpers import LogInTester


class EditProfileTestCase(TestCase, LogInTester):
    """Tests of the edit profile view"""

    def setUp(self):
        self.url = reverse('profile')
        self.login_url = reverse('log_in')
        self.username = "@johndoe"
        self.first_name = "john"
        self.last_name = "doe"
        self.email = "johndoe@test.com"
        self.bio = "My bio"
        self.password = "#NDGDR98adada123"
        self.chess_exp = "Beginner"
        self.personal_statement = "john doe personal statement"

        self.user = User.objects.create_user(
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            bio=self.bio,
            password=self.password,
            chess_exp=self.chess_exp,
            personal_statement=self.personal_statement,
        )

    def test_profile_url(self):
        self.assertEqual(self.url, '/home/profile/')

    def test_profile_is_correct(self):
        self.client.login(username='@johndoe', password='#NDGDR98adada123')
        curr_profile = self.client.get(self.url)
        profile_user = curr_profile.context["user"]
        self.assertEqual(self.username, profile_user.username)
        self.assertEqual(self.first_name, profile_user.first_name)
        self.assertEqual(self.last_name, profile_user.last_name)
        self.assertEqual(self.email, profile_user.email)
        self.assertEqual(self.bio, profile_user.bio)
        self.assertEqual(self.chess_exp, profile_user.chess_exp)
        self.assertEqual(self.personal_statement, profile_user.personal_statement)
