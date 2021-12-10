"""Unit tests of the home view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import Tournament, User, Club
from clubs.tests.views.helpers import reverse_with_next

class HomeTest(TestCase):
    """Unit tests of the home view"""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/other_users.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/default_tournament.json",
        "clubs/tests/fixtures/default_match.json",
        "clubs/tests/fixtures/other_clubs.json",
    ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.jane = User.objects.get(email="janedoe@example.com")
        self.michael = User.objects.get(email="michaeldoe@example.com")
        self.alice = User.objects.get(email="alicedoe@example.com")
        self.bob = User.objects.get(email="bobdoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.other_club = Club.objects.get(name = "Saint Louis Chess Club 2")
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")
        self.url = reverse("home_page")

    def test_home_displays_correct_upcoming_tournaments(self):
        self.client.login(email = self.michael.email, password = 'Password123')
        response = self.client.get(self.url)
        #print(response.content)
