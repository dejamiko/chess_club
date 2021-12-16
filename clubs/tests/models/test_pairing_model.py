"""Unit tests of the pairing model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Tournament, Pairing


class PairingModelTestCase(TestCase):
    """Unit tests of the pairing model."""
    fixtures = ["clubs/tests/fixtures/default_user.json", 'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json', 'clubs/tests/fixtures/other_clubs.json',
                'clubs/tests/fixtures/default_tournament.json']

    def setUp(self):
        self.pairing = Pairing.objects.create(
            white_player=User.objects.get(email='johndoe@example.com'),
            black_player=User.objects.get(email='janedoe@example.com'),
            round=1,
            tournament=Tournament.objects.get(name="Saint Louis Chess Tournament"),
        )

    def test_valid_pairing_is_valid(self):
        self._assert_pairing_is_valid()

    def test_white_player_cannot_be_null(self):
        self.pairing.white_player = None
        self._assert_pairing_is_invalid()

    def test_black_player_cannot_be_null(self):
        self.pairing.black_player = None
        self._assert_pairing_is_invalid()

    def test_tournament_cannot_be_null(self):
        self.pairing.tournament = None
        self._assert_pairing_is_invalid()

    def test_round_cannot_be_null(self):
        self.pairing.round = None
        self._assert_pairing_is_invalid()

    def test_get_other_player_when_white(self):
        self.assertEqual(self.pairing.get_other_player(self.pairing.white_player), self.pairing.black_player)

    def test_get_other_player_when_black(self):
        self.assertEqual(self.pairing.get_other_player(self.pairing.black_player), self.pairing.white_player)

    def _assert_pairing_is_valid(self):
        try:
            self.pairing.full_clean()
        except ValidationError:
            self.fail('Test pairing should be valid')

    def _assert_pairing_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.pairing.full_clean()
