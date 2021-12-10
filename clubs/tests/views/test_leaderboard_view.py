"""Unit tests of the leaderboard view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import Tournament, User, Club
from clubs.tests.views.helpers import reverse_with_next


class LeaderboardTest(TestCase):
    """Unit tests of the view leaderboard view"""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/other_users.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/default_tournament.json",
        "clubs/tests/fixtures/default_match.json",
        "clubs/tests/fixtures/other_clubs.json",
    ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.jane = User.objects.get(email="janedoe@example.com")
        self.michael = User.objects.get(email="michaeldoe@example.com")
        self.alice = User.objects.get(email="alicedoe@example.com")
        self.bob = User.objects.get(email="bobdoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.other_club = Club.objects.get(name = "Saint Louis Chess Club 2")
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")
        self.url = reverse("leaderboard", kwargs={"tournament_id": self.tournament.id})

    def test_leaderboard_url(self):
        self.assertEqual(self.url, f"/home/tournament/{self.tournament.id}/leaderboard")

    def test_get_leaderboard_with_valid_id(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leaderboard.html")
        strings_list = ['RANK', 'ELO', 'Participant', "Saint Louis Chess Tournament Leaderboard", "1", "1000", "Michael Doe", "Alice Doe"]
        for i in strings_list:
            self.assertContains(response, i)


    def test_get_leaderboard_with_invalid_id(self):
        self.client.login(email=self.user.email, password="Password123")
        url = reverse("view_tournament", kwargs={"tournament_id": self.tournament.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse("home_page")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "home_page.html")

    def test_get_leaderboard_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def create_members_for_club(self, c, user_list):
        for u in user_list:
            c.make_applicant(u)
            c.make_member(u)

    def test_leaderboard_ordering(self):
        #should be ordered based on ELO

        gabriel = User.objects.create_user(
            first_name='Gabriel',
            last_name='Doe',
            email='gabrieldoe@gmail.com',
            bio='Hi, I am Gabriel Doe',
            chess_exp='Advanced',
            personal_statement=' I, GABRIEL, love chess it is wonderful',
            elo_rating = 1100 ,
            password='Password123'
        )
        anna = User.objects.create_user(
            first_name='Anna',
            last_name='Doe',
            email='annadoe@gmail.com',
            bio='Hi, I am Anna Doe',
            chess_exp='Advanced',
            personal_statement=' I, ANNA, love chess it is wonderful',
            elo_rating = 1200 ,
            password='Password123'
        )
        aaron = User.objects.create_user(
            first_name='Aaron',
            last_name='Doe',
            email='aarondoe@gmail.com',
            bio='Hi, I am Aaron Doe',
            chess_exp='Advanced',
            personal_statement=' I, AARON, love chess it is wonderful',
            elo_rating = 900,
            password='Password123'
        )
        user_list = [gabriel, anna, aaron]
        self.create_members_for_club(self.other_club, user_list)

        new_tournament = Tournament.objects.create(
        club = self.other_club,
        name = "Test Tournament",
        description = "Test Tournament",
        organiser = self.michael,
        deadline = "9999-12-10T17:00:00+00:00"
        )

        for x in user_list:
            new_tournament.make_participant(x)

        temp_url = reverse("leaderboard", kwargs={"tournament_id": new_tournament.id})
        self.client.login(email="gabrieldoe@gmail.com", password='Password123')
        response_t = self.client.get(temp_url)
        h = str(response_t.content)
        start = r"<tr>\n\n"

        #gabriel - 1100 elo, rank 2
        gabriel_row = h[h.find(start)+len(start):h.rfind(gabriel.email)]
        test1 = """<td> 2 </td>"""
        test2 = """<td class = "elo_rating">1100</td>"""
        self.assertTrue(test1 in gabriel_row)
        self.assertTrue(test2 in gabriel_row)

        #anna - 1200 elo, rank 1
        anna_row = h[h.find(start)+len(start):h.rfind(anna.email)]
        test3 = """<td> 1 </td>"""
        test4 = """<td class = "elo_rating">1200</td>"""
        self.assertTrue(test3 in anna_row)
        self.assertTrue(test4 in anna_row)

        # aaron- 900 elo, rank 3
        aaron_row = h[h.find(start)+len(start):h.rfind(aaron.email)]
        test5 = """<td> 3 </td>"""
        test6 = """<td class = "elo_rating">900</td>"""
        self.assertTrue(test5 in aaron_row)
        self.assertTrue(test6 in aaron_row)
