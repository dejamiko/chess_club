"""Unit tests of the home view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import Tournament, User, Club
from django.utils.timezone import make_aware
from datetime import datetime
from datetime import timedelta
from clubs.tests.views.helpers import reverse_with_next


class HomeTest(TestCase):
    """Unit tests of the home view"""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/other_users.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/default_tournament.json",
        "clubs/tests/fixtures/default_match.json",
        "clubs/tests/fixtures/default_pairing.json",
        "clubs/tests/fixtures/other_clubs.json"
    ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.jane = User.objects.get(email="janedoe@example.com")
        self.michael = User.objects.get(email="michaeldoe@example.com")
        self.alice = User.objects.get(email="alicedoe@example.com")
        self.bob = User.objects.get(email="bobdoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.other_club = Club.objects.get(name="Saint Louis Chess Club 2")
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament"),
        self.url = reverse("home_page")

    def test_home_displays_correct_upcoming_tournaments(self):
        # the clubs do not have any participants, hence the need for creating one
        temp_club = Club.objects.create(
            name="Test club",
            location="London",
            description="Test club description",
            owner=self.user
        )
        user_list_temp = [self.jane, self.michael, self.alice, self.bob]

        for user2 in user_list_temp:
            temp_club.add_new_member(user2)

        temp_tournament = Tournament.objects.create(
            club=temp_club,
            name="Test tournament",
            description=" Test tournament description",
            organiser=self.user,
            deadline=make_aware(datetime.now() + timedelta(days=1))
        )

        for user3 in user_list_temp:
            temp_tournament.make_participant(user3)

        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)

        # django date format is different, hence need for splitting
        curr_date = make_aware(datetime.now() + timedelta(days=1))
        self.assertContains(response, "Test tournament")
        self.assertContains(response, "Test club")
        self.assertContains(response, "1")
        self.assertContains(response, curr_date.year)
        self.assertContains(response, curr_date.strftime("%b"))
        self.assertContains(response, curr_date.day)

    def test_home_page_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
