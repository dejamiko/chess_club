"""Unit tests of the create club form."""
from django.test import TestCase
from clubs.forms import CreateClubForm
from clubs.models import User, Club
from django import forms


class CreateClubFormTestCase(TestCase):
    """Unit tests of the create club form."""
    fixtures = ["clubs/tests/fixtures/default_user.json"]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.com')
        self.form_input = {
            'name': 'some club',
            'location': 'KCL',
            'description': 'short description here',
            'owner': self.user
        }

    def test_valid_create_club_form(self):
        form = CreateClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    # form has necessary fields
    def test_form_has_necessary_fields(self):
        form = CreateClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('description', form.fields)

    # test club name uniqueness
    def test_unique_name(self):
        form = SignUpForm(data=self.form_input)
        form_duplicate = {
            "name": "some club",
            "location": "London",
            "description": "Duplicate club :)",
        }
        second_form = SignUpForm(data=form_duplicate)
        self.assertFalse(second_form.is_valid())

    def test_form_must_save_correctly(self):
        form = CreateClubForm(data=self.form_input)
        before_count = Club.objects.count()
        form.save()
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        club = Club.objects.get(name='some club')
        self.assertEqual(club.name, 'some club')
        self.assertEqual(club.location, 'KCL')
        self.assertEqual(club.description, 'short description here')
        self.assertEqual(club.owner, self.user)
