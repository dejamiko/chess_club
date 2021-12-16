from django.test import TestCase
from clubs.models import *
from clubs.forms import CreateClubForm
from django.urls import reverse


class EloRatingModelTestCase(TestCase):
    fixtures = ["clubs/tests/fixtures/default_user.json",
                'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_clubs.json',
                "clubs/tests/fixtures/default_elo.json",
                "clubs/tests/fixtures/other_elo.json",
                "clubs/tests/fixtures/default_pairing.json",
                "clubs/tests/fixtures/default_tournament.json"
                ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.second_user = User.objects.get(email="janedoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.second_club = Club.objects.get(name="Saint Louis Chess Club 2")
        self.user_elo = EloRating.objects.get(pk=1)
        self.second_user_elo = EloRating.objects.get(pk=2)
        self.pairing = Pairing.objects.get(pk=1)
        self.michael = User.objects.get(email="michaeldoe@example.com")
        self.alice = User.objects.get(email="alicedoe@example.com")
        self.alice_elo = EloRating.objects.get(pk=5)
        self.form_input = {
            'name': 'KCL Chess Club',
            'location': 'London',
            'description': 'Chess!!!',
            'owner': self.michael
        }
        self.url = reverse('create_club')

    def test_user_has_elo(self):
        elo_test_value = EloRating.objects.get(user=self.user, club=self.club)
        self.assertEquals(self.user_elo.elo_rating, elo_test_value.elo_rating)

    def test_user_has_elo_after_joining_club(self):
        self.second_club.make_member(self.second_user)
        elo_test_value = EloRating.objects.get(user=self.second_user, club=self.second_club)
        self.assertEquals(elo_test_value.elo_rating, self.second_user_elo.elo_rating)

    def test_user_elo_after_win(self):
        pairing_to_match_group_phase(self.pairing, self.michael)
        michael_rating = EloRating.objects.get(user=self.michael, club=self.club)
        alice_rating = EloRating.objects.get(user=self.alice, club=self.club)
        self.assertEquals(michael_rating.elo_rating, 1024)
        self.assertEquals(alice_rating.elo_rating, 1175)

    def test_user_elo_after_draw(self):
        pairing_to_match_group_phase(self.pairing, None)
        michael_rating = EloRating.objects.get(user=self.michael, club=self.club)
        alice_rating = EloRating.objects.get(user=self.alice, club=self.club)
        self.assertEquals(michael_rating.elo_rating, 1008)
        self.assertEquals(alice_rating.elo_rating, 1191)

    def test_separate_elo_for_different_club(self):
        self.second_club.make_member(self.second_user)
        jane_elo_club_1 = EloRating.objects.get(user=self.second_user, club=self.club)
        jane_elo_club_2 = EloRating.objects.get(user=self.second_user, club=self.second_club)
        self.assertEquals(jane_elo_club_1.elo_rating, 1000)
        self.assertEquals(jane_elo_club_2.elo_rating, 1000)
        self.assertIsNot(jane_elo_club_1, jane_elo_club_2)

    def test_elo_exists_after_new_club_made(self):
        self.client.login(email=self.michael.email, password='Password123')
        CreateClubForm(data=self.form_input)
        self.client.post(self.url, self.form_input, follow=True)
        third_club = Club.objects.get(name='KCL Chess Club')
        michael_third_club_elo = EloRating.objects.get(user=self.michael, club=third_club)
        self.assertTrue(michael_third_club_elo.elo_rating)

    def test_assign_elo(self):
        self.user_elo.assign_elo(club=self.club, user=self.user, elo_rating=2000)
        self.assertEqual(self.user_elo.elo_rating, 2000)
