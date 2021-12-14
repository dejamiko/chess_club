"""Unit tests of the user transitions model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import Club, User


class TransitionsBetweenModelsTestCase(TestCase):
    """Unit tests of the user transitions model."""
    fixtures = ['clubs/tests/fixtures/default_user.json', 'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.user = User.objects.get(email='janedoe@example.com')
        self.club = Club.objects.get(name='Saint Louis Chess Club')

    def test_make_user_a_member(self):
        self._assert_user_is_valid()
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        self._assert_user_is_valid()

    def test_make_member_a_user(self):
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        self.club.make_user(self.user)
        # THey are no longer in the club, and must therefore reapply
        self.assertEqual(self.user.user_level(self.club), None)
        self._assert_user_is_valid()

    def test_make_member_an_officer(self):
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        self.club.make_officer(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Officer')
        self._assert_user_is_valid()

    def test_make_officer_a_member(self):
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        self.club.make_officer(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Officer')
        self.club.make_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        self._assert_user_is_valid()

    def test_make_officer_an_owner(self):
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        self.club.make_officer(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Officer')
        self.club.make_owner(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Owner')
        self._assert_user_is_valid()

    def test_make_owner_an_officer(self):
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        self.club.make_officer(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Officer')
        self.club.make_owner(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Owner')
        self.club.make_owner(User.objects.get(email='johndoe@example.com'))
        self.assertEqual(self.user.user_level(self.club), 'Officer')
        self._assert_user_is_valid()

    def test_make_user_a_user_fails(self):
        with self.assertRaises(ValueError):
            self.club.make_user(self.user)

    def test_make_officer_a_user_fails(self):
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        self.club.make_officer(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Officer')
        with self.assertRaises(ValueError):
            self.club.make_user(self.user)

    def test_make_owner_a_user_fails(self):
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        self.club.make_officer(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Officer')
        self.club.make_owner(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Owner')
        with self.assertRaises(ValueError):
            self.club.make_user(self.user)

    def test_make_member_a_member_fails(self):
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        with self.assertRaises(ValueError):
            self.club.make_member(self.user)

    def test_make_owner_a_member_fails(self):
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        self.club.make_officer(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Officer')
        self.club.make_owner(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Owner')
        with self.assertRaises(ValueError):
            self.club.make_member(self.user)

    def test_make_user_an_officer_fails(self):
        with self.assertRaises(ValueError):
            self.club.make_officer(self.user)

    def test_make_officer_an_officer_fails(self):
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        self.club.make_officer(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Officer')
        with self.assertRaises(ValueError):
            self.club.make_officer(self.user)

    def test_make_user_an_owner_fails(self):
        with self.assertRaises(ValueError):
            self.club.make_owner(self.user)

    def test_make_member_an_owner_fails(self):
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        with self.assertRaises(ValueError):
            self.club.make_owner(self.user)

    def test_make_owner_an_owner_fails(self):
        self.club.add_new_member(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Member')
        self.club.make_officer(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Officer')
        self.club.make_owner(self.user)
        self.assertEqual(self.user.user_level(self.club), 'Owner')
        with self.assertRaises(ValueError):
            self.club.make_owner(self.user)


    def test_promote_member_to_officer(self):
        self.club.add_new_member(self.user)
        self.user.promote(self.club)
        self.assertEqual(self.user.user_level(self.club), "Officer")

    def test_demote_officer_to_member(self):
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)
        self.user.demote(self.club)
        self.assertEqual(self.user.user_level(self.club), "Member")

    def test_promote_officer_fails(self):
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)
        with self.assertRaises(ValueError):
            self.user.promote(self.club)

    def test_promote_owner_fails(self):
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)
        with self.assertRaises(ValueError):
            self.user.promote(self.club)

    def test_demote_owner_fails(self):
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)
        with self.assertRaises(ValueError):
            self.user.demote(self.club)

    def test_demote_member_fails(self):
        self.club.add_new_member(self.user)
        with self.assertRaises(ValueError):
            self.user.demote(self.club)

    def test_demote_applicant_fails(self):
        with self.assertRaises(ValueError):
            self.user.demote(self.club)

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')
