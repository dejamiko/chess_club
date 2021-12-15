"""Unit tests of the tournament scheduling."""
from django.test import TestCase
from clubs.models import User, Tournament, Match
from .helpers import _create_test_users


def _create_match_from_pairing(pairing):
    if pairing.id % 2 == 0:
        match = Match.objects.create(
            pairing=pairing,
            winner=pairing.white_player,
            loser=pairing.black_player,
            is_draw=False
        )
    else:
        match = Match.objects.create(
            pairing=pairing,
            winner=pairing.black_player,
            loser=pairing.white_player,
            is_draw=False
        )
    match.save()


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
        correct_pairings = [
            [(15, 39), (23, 31), (16, 40), (24, 32), (17, 41), (25, 33), (18, 42), (26, 34), (19, 43), (27, 35),
             (20, 44), (28, 36), (29, 37), (30, 38)],
            [(39, 31), (15, 23), (40, 32), (16, 24), (41, 33), (17, 25), (42, 34), (18, 26), (43, 35), (19, 27),
             (44, 36), (20, 28), (21, 29), (22, 30)],
            [(23, 39), (31, 15), (24, 40), (32, 16), (25, 41), (33, 17), (26, 42), (34, 18), (27, 43), (35, 19),
             (28, 44), (36, 20), (37, 21), (38, 22)]
        ]

        first_pairings = self.tournament.create_initial_pairings()
        for j in range(0, len(correct_pairings[0])):
            self.assertEqual(correct_pairings[0][j][0], first_pairings[j].white_player.id)
            self.assertEqual(correct_pairings[0][j][1], first_pairings[j].black_player.id)

        second_pairings = self.tournament.next_pairings()
        for j in range(0, len(correct_pairings[1])):
            self.assertEqual(correct_pairings[1][j][0], second_pairings[j].white_player.id)
            self.assertEqual(correct_pairings[1][j][1], second_pairings[j].black_player.id)

        third_pairings = self.tournament.next_pairings()
        for j in range(0, len(correct_pairings[2])):
            self.assertEqual(correct_pairings[2][j][0], third_pairings[j].white_player.id)
            self.assertEqual(correct_pairings[2][j][1], third_pairings[j].black_player.id)

        for pairing in self.tournament.pairings_within.all():
            _create_match_from_pairing(pairing)

        correct_group_rankings = [
            [(15, 1), (23, 1), (31, 2), (39, 2)],
            [(16, 1), (24, 1), (32, 2), (40, 2)],
            [(17, 1), (25, 1), (33, 2), (41, 2)],
            [(18, 1), (26, 1), (34, 2), (42, 2)],
            [(19, 1), (27, 1), (35, 2), (43, 2)],
            [(20, 1), (28, 1), (36, 2), (44, 2)],
            [(21, 2), (29, 0), (37, 1)],
            [(22, 0), (30, 2), (38, 1)]
        ]
        correct_group_top_seeds = [
            (31, 39), (32, 40), (33, 41), (34, 42), (35, 43), (36, 44), (21, 37), (30, 38)
        ]

        for group in self.tournament.groups_within.all():
            ranking = group.get_ranking()
            ranking_list = []
            for player, points in ranking.items():
                ranking_list.append((player, points))
            for j in range(0, len(ranking)):
                self.assertEqual(ranking_list[j][0].id, correct_group_rankings[group.id - 1][j][0])
                self.assertEqual(ranking_list[j][1], correct_group_rankings[group.id - 1][j][1])
            top_seeds = group.get_top_seeds()
            self.assertEqual(top_seeds[0].id, correct_group_top_seeds[group.id - 1][0])
            self.assertEqual(top_seeds[1].id, correct_group_top_seeds[group.id - 1][1])

        correct_bracket_pairings = [
            [(31, 38), (32, 37), (33, 44), (34, 43), (35, 42), (36, 41), (21, 40), (30, 39)],
            [(38, 32), (44, 34), (42, 36), (40, 30)],
            [(32, 44), (36, 40)],
            [(44, 36)]
        ]

        for i in range(0, len(correct_bracket_pairings)):
            pairings = self.tournament.next_pairings()
            self.assertFalse(self.tournament.all_pairings_completed())

            for j in range(0, len(correct_bracket_pairings[i])):
                self.assertEqual(pairings[j].white_player.id, correct_bracket_pairings[i][j][0])
                self.assertEqual(pairings[j].black_player.id, correct_bracket_pairings[i][j][1])

            for pairing in pairings:
                _create_match_from_pairing(pairing)

    def test_tournament_with_no_groups(self):
        participants = list(User.objects.all())[10: 21]
        self.tournament.participants.set(participants)

        correct_first_pairings = [(15, 16), (17, 18), (19, 20), (21, 22), (23, 24)]

        first_pairings = self.tournament.create_initial_pairings()
        for i in range(0, len(correct_first_pairings)):
            self.assertEqual(first_pairings[i].white_player.id, correct_first_pairings[i][0])
            self.assertEqual(first_pairings[i].black_player.id, correct_first_pairings[i][1])

        for pairing in first_pairings:
            _create_match_from_pairing(pairing)

        correct_bracket_pairings = [
            [(16, 17), (20, 21), (24, 25)],
            [(16, 21)],
            [(21, 24)],
        ]

        for i in range(0, 3):
            pairings = self.tournament.next_pairings()
            for j in range(0, len(pairings)):
                self.assertEqual(pairings[j].white_player.id, correct_bracket_pairings[i][j][0])
                self.assertEqual(pairings[j].black_player.id, correct_bracket_pairings[i][j][1])

            for pairing in pairings:
                _create_match_from_pairing(pairing)
