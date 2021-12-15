"""Unit tests of the match model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import *


class MatchModelTestCase(TestCase):
    """Unit tests of the match model."""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/other_users.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/default_tournament.json",
        "clubs/tests/fixtures/default_pairing.json",
        "clubs/tests/fixtures/default_match.json",
        "clubs/tests/fixtures/default_elo.json",
        "clubs/tests/fixtures/other_elo.json"
    ]

    def setUp(self):
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")
        self.match = Match.objects.get(pk=1)
        self.pairing = Pairing.objects.get(pk=1)
        self.michael = User.objects.get(email="michaeldoe@example.com")
        self.alice = User.objects.get(email="alicedoe@example.com")
        self.michael_elo = EloRating.objects.get(pk=4)
        self.alice_elo = EloRating.objects.get(pk=5)

    def test_match_has_winner(self):
        self.assertEquals(self.match.winner, self.alice)

    def test_match_has_loser(self):
        self.assertEquals(self.match.loser, self.michael)

    def test_match_sets_winner_and_loser_correctly(self):
        self.match.winner = None
        self.match.loser = None
        test_match = pairing_to_match_group_phase(self.pairing, self.michael)
        self.assertEquals(test_match.winner, self.michael)
        self.assertEquals(test_match.loser, self.alice)

    def test_winner_can_be_blank(self):
        self.match.winner = None
        self._assert_match_is_valid()

    def test_loser_can_be_blank(self):
        self.match.loser = None
        self._assert_match_is_valid()

    def test_pairing_cannot_be_blank(self):
        self.match.pairing = None
        self._assert_match_is_invalid()

    def _assert_match_is_valid(self):
        try:
            self.match.full_clean()
        except ValidationError as error:
            self.fail(error)

    def _assert_match_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.match.full_clean()
