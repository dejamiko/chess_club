from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.test import TestCase
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from clubs.models import Tournament, User, Club, Match, Pairing
from .helpers import _create_test_users


class TournamentModelTestCase(TestCase):
    """Unit tests of the tournament model."""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/other_users.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/default_tournament.json",
        "clubs/tests/fixtures/other_tournament.json",
        "clubs/tests/fixtures/default_pairing.json",
        "clubs/tests/fixtures/default_match.json"
    ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.bob = User.objects.get(email="bobdoe@example.com")
        self.michael = User.objects.get(email="michaeldoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")
        self.other_tournament = Tournament.objects.get(name="Bedroom Tournament")
        self.match = Match.objects.get(pk=1)
        self.pairing = Pairing.objects.get(pk=1)

    def tournament_has_a_club(self):
        self.assertEquals(self.tournament.club, self.club)

    def test_name_must_be_unique(self):
        self.tournament.name = self.other_tournament.name
        self._assert_tournament_is_invalid()

    def test_name_can_be_50_characters_long(self):
        self.tournament.name = "x" * 50
        self._assert_tournament_is_valid()

    def test_name_cannot_be_over_50_characters_long(self):
        self.tournament.name = "x" * 51
        self._assert_tournament_is_invalid()

    def test_name_cannot_be_blank(self):
        self.tournament.name = ""
        self._assert_tournament_is_invalid()

    def test_description_can_be_500_characters_long(self):
        self.tournament.description = "x" * 500
        self._assert_tournament_is_valid()

    def test_description_cannot_be_over_500_characters_long(self):
        self.tournament.description = "x" * 501
        self._assert_tournament_is_invalid()

    def test_description_can_be_blank(self):
        self.tournament.description = ""
        self._assert_tournament_is_valid()

    def test_tournament_has_participants(self):
        self.assertEquals(self.tournament.get_number_of_participants(), 2)
        self.assertTrue(User.objects.get(email="michaeldoe@example.com") in self.tournament.participants.all())
        self.assertTrue(User.objects.get(email="alicedoe@example.com") in self.tournament.participants.all())

    def test_tournament_must_have_organiser(self):
        self.assertEqual(self.tournament.organiser, self.user)
        self.tournament.organiser = None
        self._assert_tournament_is_invalid()

    def test_tournament_has_coorganisers(self):
        self.assertEquals(self.tournament.coorganisers.count(), 2)
        self.assertTrue(User.objects.get(email="janedoe@example.com") in self.tournament.coorganisers.all())
        self.assertTrue(User.objects.get(email="bobdoe@example.com") in self.tournament.coorganisers.all())

    def test_tournament_with_no_coorganisers(self):
        self.tournament.coorganisers.set([])
        self._assert_tournament_is_valid()

    def test_tournament_must_have_deadline(self):
        self.tournament.deadline = None
        self._assert_tournament_is_invalid()

    def test_tournament_does_not_have_to_have_a_winner(self):
        self.assertEquals(self.tournament.winner, User.objects.get(email="alicedoe@example.com"))
        self.tournament.winner = None
        self._assert_tournament_is_valid()

    def test_tournament_has_pairings_in_it(self):
        self.assertEquals(self.tournament.pairings_within.count(), 1)
        self.assertTrue(self.pairing in self.tournament.pairings_within.all())

    def test_tournament_status_completed(self):
        self.assertEqual(self.tournament.get_status(), "Completed")

    def test_tournament_status_round(self):
        self.tournament.winner = None
        self.tournament.deadline = make_aware(datetime.today() - timedelta(days=1))
        self.tournament.save()
        self.assertEqual(self.tournament.get_status(), "Round 1")

    def test_tournament_status_applications_full(self):
        self.tournament.winner = None
        self.tournament.save()

        _create_test_users(100, 94)
        for i in range(100, 194):
            user = User.objects.get(id=i)
            self.club.add_new_member(user)
            self.tournament.participants.add(user)
        self.tournament.save()

        self.assertEqual(self.tournament.get_status(), "Applications full")

    def test_tournament_status_taking_applications(self):
        self.tournament.winner = None
        self.tournament.save()
        self.assertEqual(self.tournament.get_status(), "Taking applications")

    def test_set_tournament_winner(self):
        self.tournament.set_winner(self.bob)
        self.assertEqual(self.tournament.winner, self.bob)

    def test_make_participant(self):
        self.tournament.make_participant(self.bob)
        self.assertEqual(self.tournament.get_all_participants().get(email="bobdoe@example.com"), self.bob)

    def test_tournament_cannot_have_duplicate_participant(self):
        self.tournament.make_participant(self.bob)
        with self.assertRaises(ValueError):
            self.tournament.make_participant(self.bob)

    def test_remove_participant(self):
        self.tournament.remove_participant(self.michael)
        with self.assertRaises(ObjectDoesNotExist):
            self.tournament.get_all_participants().get(email="michaeldoe@example.com")

    def test_cannot_remove_participant_twice(self):
        self.tournament.remove_participant(self.michael)
        with self.assertRaises(ValueError):
            self.tournament.remove_participant(self.michael)

    def _assert_tournament_is_valid(self):
        try:
            self.tournament.full_clean()
        except ValidationError as error:
            self.fail(error)

    def _assert_tournament_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tournament.full_clean()
