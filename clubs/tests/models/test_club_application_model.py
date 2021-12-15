"""Unit tests of the club application model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club, ClubApplication
from django.urls import reverse


class ClubApplicationModelTestCase(TestCase):
    """Unit tests of the club application model."""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/other_users.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/other_clubs.json",
        "clubs/tests/fixtures/default_application.json",
        "clubs/tests/fixtures/other_application.json",
    ]

    def setUp(self):
        self.url = reverse("manage_applications")
        self.first_user = User.objects.get(email="johndoe@example.com")
        self.second_user = User.objects.get(email="janedoe@example.com")
        self.first_club = Club.objects.get(name="Saint Louis Chess Club")
        self.second_club = Club.objects.get(name="Saint Louis Chess Club 2")
        self.first_club_application = ClubApplication.objects.get(associated_club=self.first_club)
        self.second_club_application = ClubApplication.objects.get(associated_club=self.second_club)

    def test_club_application_always_has_an_associated_user(self):
        self.first_club_application.associated_user = None
        self._assert_club_application_is_invalid()

    def test_club_application_always_has_an_associated_club(self):
        self.first_club_application.associated_club = None
        self._assert_club_application_is_invalid()

    def _assert_club_application_is_valid(self):
        try:
            self.first_club_application.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')

    def _assert_club_application_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.first_club_application.full_clean()
