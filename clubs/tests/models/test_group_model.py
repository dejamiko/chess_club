"""Unit tests of the group model."""
from django.test import TestCase
from clubs.models import User, Tournament, Group
from .helpers import _create_test_users


class GroupModelTestCase(TestCase):
    """Unit tests of the group model."""
    fixtures = ["clubs/tests/fixtures/default_user.json", 'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json', 'clubs/tests/fixtures/other_clubs.json',
                'clubs/tests/fixtures/default_tournament.json']

    def setUp(self):
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")
        self.group = Group.objects.create(
            tournament=self.tournament,
            group_number=1,
            id=1,
        )
        self.correct_pairs = [
            [(1, 14), (2, 13), (3, 12), (4, 11), (5, 10), (6, 9), (7, 8)],
            [(14, 8), (9, 7), (10, 6), (11, 5), (12, 4), (13, 3), (1, 2)],
            [(2, 14), (3, 1), (4, 13), (5, 12), (6, 11), (7, 10), (8, 9)],
            [(14, 9), (10, 8), (11, 7), (12, 6), (13, 5), (1, 4), (2, 3)],
            [(3, 14), (4, 2), (5, 1), (6, 13), (7, 12), (8, 11), (9, 10)],
            [(14, 10), (11, 9), (12, 8), (13, 7), (1, 6), (2, 5), (3, 4)],
            [(4, 14), (5, 3), (6, 2), (7, 1), (8, 13), (9, 12), (10, 11)],
            [(14, 11), (12, 10), (13, 9), (1, 8), (2, 7), (3, 6), (4, 5)],
            [(5, 14), (6, 4), (7, 3), (8, 2), (9, 1), (10, 13), (11, 12)],
            [(14, 12), (13, 11), (1, 10), (2, 9), (3, 8), (4, 7), (5, 6)],
            [(6, 14), (7, 5), (8, 4), (9, 3), (10, 2), (11, 1), (12, 13)],
            [(14, 13), (1, 12), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)],
            [(7, 14), (8, 6), (9, 5), (10, 4), (11, 3), (12, 2), (13, 1)],
        ]

    def test_generating_pairs_for_even_number_of_participants(self):
        _create_test_users(10, 14)
        participants = list(User.objects.all())[0:14]
        self._check_pairs_for_14(participants)

    def test_generating_pairings_for_even_number_of_participants(self):
        _create_test_users(10, 14)
        participants = list(User.objects.all())[0:14]
        self.group.participants.set(participants)
        for i in range(0, int((len(participants) + 1) / 2) * 2 - 1):
            pairings = self.group.get_next_pairings()
            for j in range(0, len(pairings)):
                self.assertEqual(pairings[j].white_player, participants[self.correct_pairs[i][j][0] - 1])
                self.assertEqual(pairings[j].black_player, participants[self.correct_pairs[i][j][1] - 1])

    def test_generating_pairs_for_odd_number_of_participants(self):
        _create_test_users(10, 13)
        participants = list(User.objects.all())[0:13]
        self._check_pairs_for_14(participants)

    def test_generating_pairings_for_odd_number_of_participants(self):
        _create_test_users(10, 13)
        participants = list(User.objects.all())[0:13]
        self.group.participants.set(participants)
        for i in range(0, int((len(participants) + 1) / 2) * 2 - 1):
            pairings = self.group.get_next_pairings()
            for j in range(0, len(pairings)):
                self.assertEqual(pairings[j].white_player, participants[self.correct_pairs[i][j + 1][0] - 1])
                self.assertEqual(pairings[j].black_player, participants[self.correct_pairs[i][j + 1][1] - 1])

    def _check_pairs_for_14(self, participants):
        self.group.participants.set(participants)
        pairs = self.group.create_all_pairs()

        self.assertEqual(len(pairs), len(self.correct_pairs))
        for i in range(0, len(pairs)):
            for j in range(0, len(pairs[i])):
                self.assertEqual(pairs[i][j], self.correct_pairs[i][j])
