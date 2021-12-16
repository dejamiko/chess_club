"""Unit tests of the club list view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club
from clubs.tests.views.helpers import reverse_with_next, give_all_missing_elos


class ClubListTest(TestCase):
    """Unit tests of the club list view."""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/other_clubs.json",
    ]

    def setUp(self):
        self.url = reverse("clubs")
        self.user = User.objects.get(email="johndoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        for club in Club.objects.all():
            give_all_missing_elos(club)

    def test_pending_applications_url(self):
        self.assertEqual(self.url, "/clubs")

    def test_get_club_list(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_list.html")
        self.assertEqual(len(response.context["clubs"]), 2)
        for club in Club.objects.all():
            self.assertContains(response, club.name)
            self.assertContains(response, club.location)
            self.assertContains(response, club.description)
            self.assertContains(response, club.get_number_of_members())
            self.assertContains(response, club.owner.first_name)
            self.assertContains(response, club.owner.last_name)
            self.assertContains(response, club.owner.bio)

    def test_club_page_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
