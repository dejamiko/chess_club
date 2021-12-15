"""Unit tests of the club page view."""
from django.test import TestCase
from clubs.models import Tournament, User, Club
from django.urls import reverse
from clubs.tests.views.helpers import reverse_with_next


class ClubPageViewTest(TestCase):
    """Unit tests of the club page view."""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/other_clubs.json",
        "clubs/tests/fixtures/default_tournament.json",
        "clubs/tests/fixtures/other_users.json"
    ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.target_user = User.objects.get(email="janedoe@example.com")
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")
        self.url = reverse("club_page", kwargs={"club_id": self.club.id})
        self.club.give_elo(self.club.owner)

    def test_club_page_url(self):
        self.assertEqual(self.url, f"/club/{self.club.id}")

    def test_club_page_has_club_info(self):
        self.client.login(username=self.user.email, password="Password123")
        url = reverse("club_page", kwargs={"club_id": self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_page.html")
        self.assertContains(response, "Saint Louis Chess Club")
        self.assertContains(response, "St. Louis, Missouri")
        self.assertContains(response, "The Saint Louis Chess Club (previously named the Chess Club and Scholastic Center of Saint Louis) is a chess venue located in the Central West End in St. Louis, Missouri, United States. Opened on July 17, 2008, it contains a tournament hall and a basement broadcast studio. Classes are held at the adjacent chess-themed Kingside Diner.")
        self.assertContains(response, "<b>Number of officers:</b> 0")
        self.assertContains(response, "<b>Number of members:</b> 0")

    def test_club_page_has_tournament_info(self):
        self.client.login(username=self.user.email, password="Password123")
        url = reverse("club_page", kwargs={"club_id": self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_page.html")
        self.assertContains(response, "<b>Tournaments hosted:</b> 1")
        for tournament in self.club.get_all_tournaments():
            self.assertContains(response, tournament.name)
            self.assertContains(response, tournament.get_number_of_participants())
            self.assertContains(response, tournament.get_status())

    def test_club_page_has_owner_info(self):
        self.client.login(username=self.user.email, password="Password123")
        url = reverse("club_page", kwargs={"club_id": self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_page.html")
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Hi, I am John Doe")
        self.assertContains(response, "<b>Chess experience:</b> Beginner")
        self.assertContains(response, "<b>Elo rating in this club:</b> 1000")

    def test_club_page_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
