from django.contrib.auth.hashers import check_password
from django.test import TestCase
from clubs.forms import EditForm, SignUpForm
from clubs.models import User
from django import forms
from django.urls import reverse


class EditFormTestCase(TestCase):
    """UNit tests of the edit form."""

    def setUp(self):
        self.url = reverse('edit_profile')
        self.sign_up_url = reverse('sign_up')
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
        self.sign_up_form_input = {
            'username': '@janedoe',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@example.org',
            'bio': 'My bio',
            'chess_exp': 'Beginner',
            'personal_statement': 'jane doe personal statement',
            'new_password': '#NDGDR98adada123',
            'password_confirmation': '#NDGDR98adada123'
        }

     # form accepts valid input data
    def test_valid_edit_form(self):
        form = EditForm(data=self.sign_up_form_input)
        self.assertTrue(form.is_valid())

    def test_edit_form_contains_required_fields(self):
        form = EditForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('chess_exp', form.fields)
        self.assertIn('personal_statement', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('bio', form.fields)


    def test_form_must_save_correctly(self):
        current_user = self.user
        form = EditForm(self.sign_up_form_input, instance = current_user)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        #edit form shouldn't increase users - edits existing one
        self.assertEqual(after_count, before_count)
        user = User.objects.get(username='@janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        self.assertEqual(user.bio, 'My bio')
        self.assertEqual(user.chess_exp, 'Beginner')
        self.assertEqual(user.personal_statement, 'jane doe personal statement')