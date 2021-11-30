from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club

class SwitchClubTest(TestCase):

    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/other_clubs.json",
    ]

    def setUp(self):

        self.first_user = User.objects.get(email="johndoe@example.com")
        self.first_club = Club.objects.get(name="Saint Louis Chess Club")
        self.second_club = Club.objects.get(name="Saint Louis Chess Club 2")
        self.url = reverse("users", kwargs={'club_id': self.first_club.id})

    def test_switch_club_url(self):
        self.assertEqual(self.url, '/home/1/users/')



