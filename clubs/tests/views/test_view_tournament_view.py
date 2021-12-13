"""Unit tests of the view tournament view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import Tournament, User, Club
from clubs.tests.models.helpers import _create_test_users
from clubs.tests.views.helpers import reverse_with_next
from datetime import datetime, timedelta
from django.utils.timezone import make_aware


class ViewTournamentTest(TestCase):
    """Unit tests of the view tournament view"""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/other_users.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/default_tournament.json",
        "clubs/tests/fixtures/other_tournament.json",
        "clubs/tests/fixtures/default_match.json",
        "clubs/tests/fixtures/other_clubs.json",
        'clubs/tests/fixtures/default_pairing.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.jane = User.objects.get(email="janedoe@example.com")
        self.michael = User.objects.get(email="michaeldoe@example.com")
        self.alice = User.objects.get(email="alicedoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.other_club = Club.objects.get(name = "Saint Louis Chess Club 2")
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")
        self.other_tournament = Tournament.objects.get(name="Bedroom Tournament")
        self.url = reverse("view_tournament", kwargs={"tournament_id": self.tournament.id})

    def test_view_tournament_url(self):
        self.assertEqual(self.url, f"/home/tournament/{self.tournament.id}")

    def test_get_view_tournament_with_valid_id(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_tournament.html")

        self.assertContains(response, "Saint Louis Chess Tournament")
        self.assertContains(response,
                            "The region&#x27;s most prestigious tournament, held in our purpose-built tournament hall, with afterparty at the basement broadcast studio.")

        self.assertNotContains(response, "Pairings")
        self.assertNotContains(response, "Create pairings")
        self.assertContains(response, "Completed matches")

        for participant in response.context["tournament"].participants.all():
            self.assertContains(response, participant.full_name())
            self.assertContains(response, participant.chess_exp)

        self.assertContains(response, "John Doe")
        self.assertContains(response, "Hi, I am John Doe")

        self.assertContains(response, "Saint Louis Chess Club")
        self.assertContains(response,
                            "The Saint Louis Chess Club (previously named the Chess Club and Scholastic Center of Saint Louis) is a chess venue located in the Central West End in St. Louis, Missouri, United States. Opened on July 17, 2008, it contains a tournament hall and a basement broadcast studio. Classes are held at the adjacent chess-themed Kingside Diner.")

        for coorganiser in response.context["tournament"].coorganisers.all():
            self.assertContains(response, coorganiser.full_name())
        self.assertContains(response, "Dec. 10, 9999, 5 p.m.")

        deadline_passed = response.context["deadline_passed"]
        self.assertFalse(deadline_passed)

    def test_get_view_tournament_with_invalid_id(self):
        self.client.login(email=self.user.email, password="Password123")
        url = reverse("view_tournament", kwargs={"tournament_id": self.tournament.id + 9999})
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

    def test_no_join_buttons_if_organiser(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Join")
        self.assertNotContains(response, "Joined!")
        self.assertNotContains(response, "Leave?")

    def test_join_buttons_if_not_participant_but_in_club(self):
        self.client.login(email=self.jane.email, password="Password123")
        self.club.make_applicant(self.jane)
        self.club.make_member(self.jane)
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

    def test_user_can_join_tournament_before_deadline(self):
        self.client.login(email=self.jane.email, password="Password123")
        self.club.make_applicant(self.jane)
        self.club.make_member(self.jane)
        tournament_before_join = Tournament.objects.get(name = "Saint Louis Chess Tournament")
        self.assertNotIn(self.jane, tournament_before_join.get_all_participants())
        response = self.client.post(self.url, {'Join_tournament': True})
        tournament_after_join = Tournament.objects.get(name = "Saint Louis Chess Tournament")
        self.assertIn(self.jane, tournament_after_join.get_all_participants())

    def test_user_can_leave_tournament_before_deadline(self):
        self.client.login(email=self.michael.email, password="Password123")
        self.club.make_applicant(self.michael)
        self.club.make_member(self.michael)
        tournament_before_leave = Tournament.objects.get(name = "Saint Louis Chess Tournament")
        self.assertIn(self.michael, tournament_before_leave.get_all_participants())
        response = self.client.post(self.url, {'Leave_tournament': True})
        tournament_after_leave = Tournament.objects.get(name = "Saint Louis Chess Tournament")
        self.assertNotIn(self.michael, tournament_after_leave.get_all_participants())
    
    def test_user_cannot_join_if_96_participants(self):
        self.client.login(email=self.user.email, password="Password123")

        _create_test_users(100, 94)
        for i in range(100, 194):
            user = User.objects.get(id=i)
            self.club.make_applicant(user)
            self.club.make_member(user)
            self.other_tournament.participants.add(user)
        self.other_tournament.save()
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Join")

    def create_two_members_for_club(self, c, user1, user2):
        c.make_applicant(user1)
        c.make_member(user1)
        c.make_applicant(user2)
        c.make_member(user2)

    def test_user_cannot_join_tournament_after_deadline(self):

        self.create_two_members_for_club(self.other_club, self.jane, self.michael)
        # create a time that is 5 minutes before current time
        d = datetime.now() - timedelta(minutes = 5)
        make_aware_date = make_aware(d)

        late_tournament = Tournament.objects.create(
        club = self.other_club,
        name = "Late Tournament",
        description = "This tournament's deadline has passed",
        organiser = self.user,
        deadline = make_aware_date
        )
        late_tournament.make_participant(self.jane)
        late_tournament.make_participant(self.michael)
        late_tournament.save()

        self.client.login(username="alicedoe@example.com", password = 'Password123')
        late_t_url = reverse("view_tournament", kwargs={"tournament_id": late_tournament.id})
        self.other_club.make_applicant(self.alice)
        self.other_club.make_member(self.alice)

        # before joining, should  not be in tournament
        self.assertNotIn(self.alice, late_tournament.get_all_participants())
        response = self.client.post(late_t_url, {'Join_tournament': True})
        # after joining, should not be in tournament also
        self.assertNotIn(self.alice, late_tournament.get_all_participants())

    def test_user_cannot_leave_tournament_after_deadline(self):

        self.create_two_members_for_club(self.other_club, self.jane, self.michael)
        # create a time that is 5 minutes before current time
        d = datetime.now() - timedelta(minutes = 5)
        make_aware_date = make_aware(d)

        late_tournament = Tournament.objects.create(
        club = self.other_club,
        name = "Late Tournament",
        description = "This tournament's deadline has passed",
        organiser = self.user,
        deadline = make_aware_date
        )
        late_tournament.make_participant(self.jane)
        late_tournament.make_participant(self.michael)
        late_tournament.save()

        self.client.login(username="janedoe@example.com", password = 'Password123')
        late_t_url = reverse("view_tournament", kwargs={"tournament_id": late_tournament.id})

        # before joining, should be in tournament
        self.assertIn(self.jane, late_tournament.get_all_participants())
        response = self.client.post(late_t_url, {'Leave_tournament': True})
        # after joining, should still be in tournament
        self.assertIn(self.jane, late_tournament.get_all_participants())
