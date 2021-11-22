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
        self.url = reverse('edit_profile')
        self.login_url = reverse('log_in')
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


    def test_edit_profile_url(self):
        self.assertEqual(self.url, '/home/profile/edit/')


    def test_edit_profile_changes_attributes(self):
        self.client.login(username='@johndoe', password='#NDGDR98adada123')

        new_username='@NOTjohndoe'
        new_first_name='NOTJohn'
        new_last_name='NOTdoe'
        new_email='NOTjohndoe@test.com'
        new_bio='NOT my bio'
        new_chess_exp='Advanced'
        new_personal_statement='NOT john doe personal statement'

        edit_profile_form_input =  { 'username': new_username , 'first_name' : new_first_name,
        'last_name': new_last_name, 'email' : new_email, 'bio' : new_bio, 'chess_exp' : new_chess_exp,
        'personal_statement' :new_personal_statement
        }

        self.client.post(self.url, edit_profile_form_input)
        temp_user = User.objects.get(first_name='NOTJohn')

        self.assertEqual(temp_user.username, new_username)
        self.assertEqual(temp_user.first_name, new_first_name)
        self.assertEqual(temp_user.last_name, new_last_name)
        self.assertEqual(temp_user.email,new_email )
        self.assertEqual(temp_user.bio,new_bio )
        self.assertEqual(temp_user.chess_exp, new_chess_exp)
        self.assertEqual(temp_user.personal_statement, new_personal_statement)
