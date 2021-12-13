"""Unit tests of the profile view"""
from django.test import TestCase
from clubs.models import Tournament, User, Club, EloRating
from django.urls import reverse
from clubs.tests.views.helpers import reverse_with_next
import clubs.views

class ProfileViewTest(TestCase):
    """Unit tests of the profile view"""
    fixtures = ["clubs/tests/fixtures/default_user.json", "clubs/tests/fixtures/other_users.json",
                "clubs/tests/fixtures/default_club.json", "clubs/tests/fixtures/default_tournament.json",
                "clubs/tests/fixtures/default_elo.json",
                "clubs/tests/fixtures/other_elo.json"]

    def setUp(self):
        EloRating.objects.filter(pk=2).delete()
        self.user = User.objects.get(email="johndoe@example.com")
        self.target_user = User.objects.get(email="janedoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")
        clubs.views.club = None
        self.url = reverse("profile", kwargs={"user_id": self.target_user.id})

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_profile_url(self):
        self.assertEqual(self.url, f"/home/profile/{self.target_user.id}")

    def test_get_profile_with_valid_id(self):
        self.client.login(email=self.user.email, password="Password123")

        self.club.make_applicant(self.target_user)
        self.club.make_member(self.target_user)
        self.club.make_officer(self.target_user)
        self.tournament.participants.add(self.target_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "Hi, I&#x27;m Jane Doe")
        self.assertContains(response, "Saint Louis Chess Club")
        self.assertContains(response, "Officer")
        self.assertContains(response, "<b>Number of clubs:</b> 1")
        self.assertContains(response, "Saint Louis Chess Tournament")
        self.assertContains(response, "<b>Tournaments participated in:</b> 1")
        self.assertContains(response, "<b>Tournaments won:</b> 0")

    def test_get_profile_with_own_id(self):
        self.client.login(email=self.user.email, password="Password123")
        url = reverse("profile", kwargs={"user_id": self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Hi, I am John Doe")

    def test_get_profile_with_invalid_id_and_club_selected(self):
        self.client.login(username=self.user.email, password="Password123")
        clubs.views.club = self.club
        url = reverse("profile", kwargs={"user_id": self.user.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse("users", kwargs={"club_id": self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "user_list.html")
    
    def test_get_profile_with_invalid_id_and_no_club_selected(self):
        self.client.login(username=self.user.email, password="Password123")
        url = reverse("profile", kwargs={"user_id": self.user.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse("select_club")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "select_club_screen.html")
    
    def test_own_profile_has_email_address(self):
        self.client.login(email=self.user.email, password="Password123")
        url = reverse("profile", kwargs={"user_id": self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")
        self.assertContains(response, "johndoe@example.com")

    def test_own_profile_has_edit_button(self):
        self.client.login(email=self.user.email, password="Password123")
        url = reverse("profile", kwargs={"user_id": self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")
        self.assertContains(response, "Edit profile")

    def test_no_clubs_section_if_user_has_no_clubs(self):
        self.client.login(email=self.target_user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Saint Louis Chess Club")
        self.assertNotContains(response, "Officer")

    def test_no_tournaments_section_if_user_has_no_tournaments(self):
        self.client.login(email=self.target_user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Saint Louis Chess Tournament")
        self.assertNotContains(response, "Officer")