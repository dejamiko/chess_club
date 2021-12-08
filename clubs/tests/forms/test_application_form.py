"""Unit tests of the club application model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club, ClubApplicationModel
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
        self.first_club_application = ClubApplicationModel.objects.get(associated_club=self.first_club)
        self.second_club_application = ClubApplicationModel.objects.get(associated_club=self.second_club)

    def test_submit_creates_application(self):
        pass

    def test_accept_application_deletes_application(self):
        pass

    def test_reject_application_sets_rejected(self):
        pass

    def test_user_can_submit_multiple_applications(self):
        pass
