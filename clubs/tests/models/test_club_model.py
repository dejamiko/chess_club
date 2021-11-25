from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club


class ClubModelTestCase(TestCase):
    fixtures = ["clubs/tests/fixtures/default_user.json", 'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json', 'clubs/tests/fixtures/other_clubs.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.com')
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.other_club = Club.objects.get(name="Saint Louis Chess Club 2")
        self.jane = User.objects.get(username='janedoe')

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

    def test_club_can_have_members(self):
        self.club.make_member(self.jane)
        self.assertEqual(self.club.get_number_of_members(), 1)
        self.assertEqual(self.club.get_members().get(username='janedoe'), self.jane)

    def test_club_can_have_officers(self):
        self.club.make_member(self.jane)
        self.club.make_officer(self.jane)
        self.assertEqual(self.club.get_number_of_officers(), 1)
        self.assertEqual(self.club.get_number_of_members(), 0)
        self.assertEqual(self.club.get_officers().get(username=self.jane.username), self.jane)

    def test_club_can_change_owners(self):
        self.club.make_member(self.jane)
        self.club.make_officer(self.jane)
        self.club.make_owner(self.jane)
        self.assertEqual(self.club.get_number_of_members(), 0)
        self.assertEqual(self.club.get_number_of_officers(), 1)
        self.assertEqual(self.club.get_officers().get(username=self.user.username), self.user)
        self.assertEqual(self.club.get_owner(), self.jane)


    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()