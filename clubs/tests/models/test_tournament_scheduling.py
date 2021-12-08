"""Unit tests of the tournament scheduling."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club, Tournament, Pairing
from .helpers import _create_test_users


class TournamentSchedulingTestCase(TestCase):
    """Unit tests of the tournament scheduling."""
    fixtures = ["clubs/tests/fixtures/default_user.json", 'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json', 'clubs/tests/fixtures/other_clubs.json',
                'clubs/tests/fixtures/default_tournament.json']

    def setUp(self):
        _create_test_users(10, 35)
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")

    def test_tournament_with_group_stage(self):
        participants = list(User.objects.all())[10: 45]
        self.tournament.participants.set(participants)
        first_pairings = self.tournament.create_initial_pairings()
        print(len(first_pairings))
        correct_pairings = [
            [(15, 39), (23, 31), (16, 40), (24, 32), (17, 41), (25, 33), (18, 42), (26, 34), (19, 43), (27, 35),
             (20, 44), (28, 36), (29, 37), (30, 38)],
        ]

        for pairing in first_pairings:
            print(f'{pairing.white_player.id}, {pairing.black_player.id}')

        for i in range(0, len(correct_pairings)):
            self.assertEqual(correct_pairings[0][i][0], first_pairings[i].white_player.id)
            self.assertEqual(correct_pairings[0][i][1], first_pairings[i].black_player.id)

        second_pairings = self.tournament.next_pairings()
        for pairing in second_pairings:
            print(f'{pairing.white_player.id}, {pairing.black_player.id}')


# 0, 15@test.com
# 0, 23@test.com
# 0, 31@test.com
# 0, 39@test.com
# 1, 16@test.com
# 1, 24@test.com
# 1, 32@test.com
# 1, 40@test.com
# 2, 17@test.com
# 2, 25@test.com
# 2, 33@test.com
# 2, 41@test.com
# 3, 18@test.com
# 3, 26@test.com
# 3, 34@test.com
# 3, 42@test.com
# 4, 19@test.com
# 4, 27@test.com
# 4, 35@test.com
# 4, 43@test.com
# 5, 20@test.com
# 5, 28@test.com
# 5, 36@test.com
# 5, 44@test.com
# 6, 21@test.com
# 6, 29@test.com
# 6, 37@test.com
# 7, 22@test.com
# 7, 30@test.com
# 7, 38@test.com
