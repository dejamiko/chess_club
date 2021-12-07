from django.test import TestCase
from django.urls import reverse
from clubs.models import Tournament, User, Club
from clubs.tests.views.helpers import reverse_with_next

class ViewTournamentTest(TestCase):
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/other_users.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/default_tournament.json",
        "clubs/tests/fixtures/default_match.json"
    ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.jane = User.objects.get(email="janedoe@example.com")
        self.michael = User.objects.get(email="michaeldoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")
        self.url = reverse("view_tournament", kwargs={"tournament_id": self.tournament.id})

    def test_view_tournament_url(self):
        self.assertEqual(self.url, f"/home/tournament/{self.tournament.id}")

    def test_get_view_tournament_with_valid_id(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_tournament.html")

        self.assertContains(response, "Saint Louis Chess Tournament")
        self.assertContains(response, "The region&#x27;s most prestigious tournament, held in our purpose-built tournament hall, with afterparty at the basement broadcast studio.")
        self.assertContains(response, "MATCHES WILL BE SHOWN HERE")

        for participant in response.context["tournament"].participants.all():
            self.assertContains(response, participant.full_name())
            self.assertContains(response, participant.chess_exp)
            self.assertContains(response, participant.elo_rating)
        
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Hi, I am John Doe")

        self.assertContains(response, "Saint Louis Chess Club")
        self.assertContains(response, "The Saint Louis Chess Club (previously named the Chess Club and Scholastic Center of Saint Louis) is a chess venue located in the Central West End in St. Louis, Missouri, United States. Opened on July 17, 2008, it contains a tournament hall and a basement broadcast studio. Classes are held at the adjacent chess-themed Kingside Diner.")

        for coorganiser in response.context["tournament"].coorganisers.all():
            self.assertContains(response, coorganiser.full_name())
        self.assertContains(response, "Dec. 10, 9999, 5 p.m.")
        
        deadline_passed = response.context["deadline_passed"]
        self.assertFalse(deadline_passed)
    
    def test_get_view_tournament_with_invalid_id(self):
        self.client.login(email=self.user.email, password="Password123")
        url = reverse("view_tournament", kwargs={"tournament_id": self.tournament.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse("home_page")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "home_page.html")
    
    def test_get_view_tournament_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_no_join_buttons_if_not_in_club(self):
        self.client.login(email=self.jane.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Join")
        self.assertNotContains(response, "Joined!")
        self.assertNotContains(response, "Leave?")

    def test_join_buttons_if_not_participant(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Join")

    def test_join_buttons_if_already_participant(self):
        self.client.login(email=self.michael.email, password="Password123")
        self.club.make_applicant(self.michael)
        self.club.make_member(self.michael)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Joined!")
        self.assertContains(response, "Leave?")