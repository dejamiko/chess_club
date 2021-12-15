"""Unit tests of the create tournament view"""
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from clubs.models import User, Club, Tournament
from clubs.forms import CreateTournamentForm
import clubs.views
from datetime import datetime
from clubs.tests.views.helpers import reverse_with_next

class CreateTournamentViewTest(TestCase):
    """Unit tests of the create tournament view"""
    fixtures = ["clubs/tests/fixtures/default_user.json",
                "clubs/tests/fixtures/other_users.json",
                "clubs/tests/fixtures/default_club.json"]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.jane = User.objects.get(email="janedoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        clubs.views.club = None
        self.url = reverse("create_tournament")
        self.form_input = {
            "club": self.club,
            "name": "Saint Louis Chess Tournament",
            "description": "An example chess tournament!",
            "organiser": self.user,
            "coorganisers": [self.jane],
            "deadline_date": "10/12/2021",
            "deadline_time": "12:30"
        }

    def test_create_tournament_url(self):
        self.assertEqual(self.url, "/create_tournament")

    def test_get_create_tournament_without_club_selected(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "no_access_screen.html")

    def test_get_create_tournament_with_club_selected_when_not_officer(self):
        self.client.login(email=self.jane.email, password="Password123")
        clubs.views.club = self.club
        self.club.make_applicant(self.jane)
        self.club.make_member(self.jane)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home_page.html")

    def test_get_create_tournament_with_club_selected_when_owner(self):
        self.client.login(email=self.user.email, password="Password123")
        clubs.views.club = self.club
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_tournament.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, CreateTournamentForm))
        self.assertFalse(form.is_bound)

    def test_get_create_tournament_with_club_selected_when_officer(self):
        self.client.login(email=self.jane.email, password="Password123")
        clubs.views.club = self.club
        self.club.make_member(self.jane)
        self.club.make_officer(self.jane)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_tournament.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, CreateTournamentForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_create_tournament(self):
        self.client.login(email=self.user.email, password="Password123")
        clubs.views.club = self.club
        self.club.make_member(self.jane)
        self.club.make_officer(self.jane)
        before_count = Tournament.objects.count()
        self.form_input["name"] = ""
        response = self.client.post(self.url, self.form_input)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_tournament.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, CreateTournamentForm))
        self.assertTrue(form.is_bound)

    def test_successful_create_tournament(self):
        self.client.login(email=self.user.email, password="Password123")
        clubs.views.club = self.club
        self.club.make_member(self.jane)
        self.club.make_officer(self.jane)
        self.club.give_elo(self.user)
        before_count = Tournament.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count+1)
        new_tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")
        response_url = reverse("view_tournament", kwargs={"tournament_id":new_tournament.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertEqual(new_tournament.club, self.club)
        self.assertEqual(new_tournament.name, "Saint Louis Chess Tournament")
        self.assertEqual(new_tournament.description, "An example chess tournament!")
        self.assertEqual(new_tournament.organiser, self.user)
        self.assertEqual(list(new_tournament.coorganisers.all()), [self.jane])
        self.assertEqual(new_tournament.deadline, make_aware(datetime(2021, 10, 12, 12, 30)))

    def test_club_page_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
