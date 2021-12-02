"""Unit tests of the switch club view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club
from clubs.tests.views.helpers import reverse_with_next


class SwitchClubViewTest(TestCase):
    """Unit tests of the switch club view"""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/other_clubs.json",
        "clubs/tests/fixtures/other_users.json",
    ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.other_user = User.objects.get(email="janedoe@example.com")
        self.first_club = Club.objects.get(name="Saint Louis Chess Club")
        self.second_club = Club.objects.get(name="Saint Louis Chess Club 2")
        self.url = reverse("users", kwargs={'club_id': self.first_club.id})

    def test_club_url(self):
        self.assertEqual(self.url, '/home/1/users/')

    def test_switch_club_url(self):
        self.url = reverse("users", kwargs={'club_id': self.second_club.id})
        self.assertEqual(self.url, '/home/2/users/')

    def test_no_club(self):
        self.url = reverse("no_club")
        self.assertEqual(self.url, '/home/no_club')

    def test_select_club(self):
        self.url = reverse("select_club")
        self.assertEqual(self.url, '/home/select_club')

    def test_log_in_redirect(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_no_club_user(self):
        self.client.login(email=self.other_user.email, password="Password123")
        response = self.client.get("/home/no_club")
        self.assertTemplateUsed(response, "no_club_screen.html")

    def test_select_club_user(self):
        self.client.login(email=self.other_user.email, password="Password123")
        response = self.client.get("/home/select_club")
        self.assertTemplateUsed(response, "select_club_screen.html")

    def test_non_existent_club(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get("/home/99/users/")
        self.assertTemplateUsed(response, "no_access_screen.html")

    def test_not_member_of_club(self):
        self.client.login(email=self.other_user.email, password="Password123")
        response = self.client.get("/home/1/users/")
        self.assertTemplateUsed(response, "no_access_screen.html")

    def test_user_clubs_list(self):
        test_user_clubs = []
        test_clubs = Club.objects.all()
        for temp_club in test_clubs:
            if self.user in temp_club.get_all_users():
                test_user_clubs.append(temp_club)
        number_of_clubs = len(test_user_clubs)
        expected_clubs_list = [self.first_club, self.second_club]
        self.assertEqual(number_of_clubs, 2)
        self.assertEqual(test_user_clubs, expected_clubs_list)
