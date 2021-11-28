"""Unit tests of the sign up form."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from clubs.forms import SignUpForm
from clubs.models import User
from django import forms


class SignUpFormTestCase(TestCase):
    """Unit tests of the sign up form."""

    def setUp(self):
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@example.org',
            'bio': 'My bio',
            'chess_exp': 'Beginner',
            'personal_statement': 'jane doe personal statement',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    # form accepts valid input data
    def test_valid_sign_up_form(self):
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    # #form users model validation
    # def test_form_uses_model_validation(self):
    #     self.form_input['password'] = 'password'
    #     form = SignUpForm(data=self.form_input)
    #     self.assertFalse(form.is_valid())

    # form has necessary fields
    def test_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('chess_exp', form.fields)
        self.assertIn('personal_statement', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('bio', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)
        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        password_confirmation_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))

    # test email uniqueness
    def test_unique_email(self):
        form = SignUpForm(data=self.form_input)
        form_duplicate = {
            'first_name': 'jane2',
            'last_name': 'Doe2',
            'email': 'janedoe2@example.org',
            'bio': 'My bio2',
            'chess_exp': 'Beginner2',
            'personal_statement': 'jane doe personal statement2',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }
        form2 = SignUpForm(data=form_duplicate)
        self.assertFalse(form2.is_valid())

    # new password has correct format
    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'Password'
        self.form_input['password_confirmation'] = 'Password'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'notPassword123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = SignUpForm(data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        user = User.objects.get(email='janedoe@example.org')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        self.assertEqual(user.bio, 'My bio')
        self.assertEqual(user.chess_exp, 'Beginner')
        self.assertEqual(user.personal_statement, 'jane doe personal statement')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
