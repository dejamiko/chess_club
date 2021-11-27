from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club


class ClubListTest(TestCase):
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/other_clubs.json",
    ]

    def setUp(self):
        self.url = reverse("clubs")
        self.user = User.objects.get(email="johndoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")

    def test_pending_applications_url(self):
        self.assertEqual(self.url, "/home/clubs/")

    def test_get_user_list(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pending_applications.html")
        self.assertEqual(len(response.context["clubs"]), 2)
        for club in Club.objects.all():
            self.assertContains(response, club.name)
            self.assertContains(response, club.location)
            self.assertContains(response, club.description)
            self.assertContains(response, club.get_number_of_members())
            self.assertContains(response, club.owner.first_name)
            self.assertContains(response, club.owner.last_name)
            self.assertContains(response, club.owner.bio)
