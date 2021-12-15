"""Unit tests of the club model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club, Tournament
from clubs.tests.views.helpers import give_all_missing_elos


class ClubModelTestCase(TestCase):
    """Unit tests of the club model."""
    fixtures = ["clubs/tests/fixtures/default_user.json", 'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json', 'clubs/tests/fixtures/other_clubs.json',
                'clubs/tests/fixtures/default_tournament.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.com')
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.other_club = Club.objects.get(name="Saint Louis Chess Club 2")
        self.jane = User.objects.get(email='janedoe@example.com')
        self.tournament = Tournament.objects.get(name='Saint Louis Chess Tournament')

    def test_name_must_be_unique(self):
        self.club.name = self.other_club.name
        self._assert_club_is_invalid()

    def test_name_can_be_50_characters_long(self):
        self.club.name = 'x' * 50
        self._assert_club_is_valid()

    def test_name_cannot_be_over_50_characters_long(self):
        self.club.name = 'x' * 51
        self._assert_club_is_invalid()

    def test_name_cannot_be_blank(self):
        self.club.name = ''
        self._assert_club_is_invalid()

    def test_location_cannot_be_blank(self):
        self.club.location = ''
        self._assert_club_is_invalid()

    def test_location_can_be_100_characters_long(self):
        self.club.location = 'x' * 100
        self._assert_club_is_valid()

    def test_location_cannot_be_over_100_characters_long(self):
        self.club.location = 'x' * 101
        self._assert_club_is_invalid()

    def test_description_can_be_blank(self):
        self.club.description = ''
        self._assert_club_is_valid()

    def test_description_can_be_500_characters_long(self):
        self.club.description = 'x' * 500
        self._assert_club_is_valid()

    def test_description_cannot_be_over_500_characters_long(self):
        self.club.description = 'x' * 501
        self._assert_club_is_invalid()

    def test_club_always_has_an_owner(self):
        self.club.owner = None
        self._assert_club_is_invalid()

    def test_club_can_accept_applicant(self):
        self.club.make_applicant(self.jane)
        self.assertEqual(self.club.applicants.count(), 1)
        self.assertEqual(self.club.get_all_applicants().get(email='janedoe@example.com'), self.jane)

    def test_club_cannot_have_same_applicant_twice(self):
        self.club.make_applicant(self.jane)
        with self.assertRaises(ValueError):
            self.club.make_applicant(self.jane)

    def test_club_can_have_members(self):
        self.club.make_member(self.jane)
        self.assertEqual(self.club.get_number_of_members(), 1)
        self.assertEqual(self.club.get_members().get(email='janedoe@example.com'), self.jane)

    def test_club_can_have_officers(self):
        self.club.make_member(self.jane)
        self.club.make_officer(self.jane)
        self.assertEqual(self.club.get_number_of_officers(), 1)
        self.assertEqual(self.club.get_number_of_members(), 0)
        self.assertEqual(self.club.get_officers().get(email=self.jane.email), self.jane)

    def test_club_can_change_owners(self):
        self.club.make_member(self.jane)
        self.club.make_officer(self.jane)
        self.club.make_owner(self.jane)
        self.assertEqual(self.club.get_number_of_members(), 0)
        self.assertEqual(self.club.get_number_of_officers(), 1)
        self.assertEqual(self.club.get_officers().get(email=self.user.email), self.user)
        self.assertEqual(self.club.get_owner(), self.jane)

    def test_club_has_tournaments(self):
        self.assertTrue(self.tournament in self.club.get_all_tournaments())
        self.assertEquals(self.club.get_number_of_tournaments(), 1)
    
    def test_club_has_non_applicants(self):
        self.assertEqual(self.club.get_all_non_applicants().count(), 5)

    def test_club_average_elo(self):
        give_all_missing_elos(self.club)
        self.assertEqual(self.club.get_average_elo(), 1000)

    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()
