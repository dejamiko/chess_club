"""Unit tests of the club list view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, ClubApplication
from clubs.tests.views.helpers import give_all_missing_elos


class ClubListTest(TestCase):
    """Unit tests of the club list view."""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/other_clubs.json",
        "clubs/tests/fixtures/other_users.json"
    ]

    def setUp(self):
        self.url = reverse("clubs")
        self.manage_url = reverse("manage_applications")
        self.user = User.objects.get(email="johndoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.bob = User.objects.get(email="bobdoe@example.com")
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

    def test_apply_to_club(self):
        self.client.login(email=self.bob.email, password='Password123')
        before_count = ClubApplication.objects.count()
        self.client.post(self.url, {'name' : self.club.name})
        after_count = ClubApplication.objects.count()
        self.assertEqual(before_count+1, after_count)
        temp_application = ClubApplication.objects.get(associated_club = self.club,
        associated_user = self.bob)
        self.assertEqual(self.club, temp_application.associated_club)
        self.assertEqual(self.bob, temp_application.associated_user)

    def test_cannot_apply_to_club_twice(self):
        self.client.login(email=self.bob.email, password='Password123')
        before_count = ClubApplication.objects.count()
        self.client.post(self.url, {'name' : self.club.name})
        after_count = ClubApplication.objects.count()
        self.assertEqual(before_count+1, after_count)
        temp_application = ClubApplication.objects.get(associated_club = self.club,
        associated_user = self.bob)
        self.assertEqual(self.club, temp_application.associated_club)
        self.assertEqual(self.bob, temp_application.associated_user)
        before_count2 = ClubApplication.objects.count()
        self.client.post(self.url, {'name' : self.club.name})
        after_count2 = ClubApplication.objects.count()
        self.assertEqual(before_count2, after_count2)

    def test_cannot_apply_when_rejected(self):
        self.client.login(email=self.bob.email, password='Password123')
        self.client.post(self.url, {'name' : self.club.name})
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
        self.client.post(self.url, {'name' : self.club.name})
        after_count = ClubApplication.objects.count()
        self.assertEqual(before_count, after_count)
