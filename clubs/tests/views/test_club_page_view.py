"""Unit tests of the club page view."""
from django.test import TestCase
from clubs.models import Tournament, User, Club, ClubApplication, EloRating
from django.urls import reverse
from clubs.tests.views.helpers import reverse_with_next
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

class ClubPageViewTest(TestCase):
    """Unit tests of the club page view."""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/other_clubs.json",
        "clubs/tests/fixtures/default_tournament.json",
        "clubs/tests/fixtures/other_tournament.json",
        "clubs/tests/fixtures/other_users.json"
    ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.bob = User.objects.get(email="bobdoe@example.com")
        self.alice = User.objects.get(email='alicedoe@example.com')
        self.michael = User.objects.get(email='michaeldoe@example.com')
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.other_club = Club.objects.get(name="Saint Louis Chess Club 2")
        self.target_user = User.objects.get(email="janedoe@example.com")
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")
        self.other_tournament = Tournament.objects.get(name="Bedroom Tournament")
        self.url = reverse("club_page", kwargs={"club_id": self.club.id})
        self.manage_url = reverse("manage_applications")
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
        self.assertContains(response, "<b>Tournaments hosted:</b> 2")
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

    def test_apply_to_club(self):
        self.client.login(email=self.bob.email, password='Password123')
        before_count = ClubApplication.objects.count()
        self.client.post(self.url)
        after_count = ClubApplication.objects.count()
        self.assertEqual(before_count+1, after_count)
        temp_application = ClubApplication.objects.get(associated_club = self.club,
        associated_user = self.bob)
        self.assertEqual(self.club, temp_application.associated_club)
        self.assertEqual(self.bob, temp_application.associated_user)

    def test_cannot_apply_to_club_twice(self):
        self.client.login(email=self.bob.email, password='Password123')
        before_count = ClubApplication.objects.count()
        self.client.post(self.url)
        after_count = ClubApplication.objects.count()
        self.assertEqual(before_count+1, after_count)
        temp_application = ClubApplication.objects.get(associated_club = self.club,
        associated_user = self.bob)
        self.assertEqual(self.club, temp_application.associated_club)
        self.assertEqual(self.bob, temp_application.associated_user)
        before_count2 = ClubApplication.objects.count()
        self.client.post(self.url)
        after_count2 = ClubApplication.objects.count()
        self.assertEqual(before_count2, after_count2)

    def test_cannot_apply_when_rejected(self):
        self.client.login(email=self.bob.email, password='Password123')
        self.client.post(self.url)
        self.client.logout()
        self.client.login(email= self.user.email, password='Password123')
        self.client.post(self.manage_url, {'uname' : self.bob.email,
        'clubname': self.club.name, 'rejected': True})
        self.client.logout()
        temp_application = ClubApplication.objects.get(associated_club = self.club,
        associated_user = self.bob)
        self.assertEqual(temp_application.is_rejected, True)
        before_count = ClubApplication.objects.count()
        self.client.login(email=self.bob.email, password='Password123')
        self.client.post(self.url)
        after_count = ClubApplication.objects.count()
        self.assertEqual(before_count, after_count)
