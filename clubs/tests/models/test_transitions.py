from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, make_member, make_user, make_officer, make_owner


class TransitionsBetweenModelsTestCase(TestCase):
    fixtures = ['clubs/tests/fixtures/default_user.json', 'clubs/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.com')

    def test_make_user_a_member(self):
        self._assert_user_is_valid()
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        self._assert_user_is_valid()

    def test_make_member_a_user(self):
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        self.user = make_user(self.user)
        self.assertEqual(self.user.user_level, "Applicant")
        self._assert_user_is_valid()

    def test_make_member_an_officer(self):
        self._assert_user_is_valid()
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        self.user = make_officer(self.user)
        self.assertEqual(self.user.user_level, "Officer")
        self._assert_user_is_valid()

    def test_make_officer_a_member(self):
        self._assert_user_is_valid()
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        self.user = make_officer(self.user)
        self.assertEqual(self.user.user_level, "Officer")
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        self._assert_user_is_valid()

    def test_make_officer_an_owner(self):
        self._assert_user_is_valid()
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        self.user = make_officer(self.user)
        self.assertEqual(self.user.user_level, "Officer")
        self.user = make_owner(self.user)
        self.assertEqual(self.user.user_level, "Owner")
        self._assert_user_is_valid()

    def test_make_owner_an_officer(self):
        self._assert_user_is_valid()
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        self.user = make_officer(self.user)
        self.assertEqual(self.user.user_level, "Officer")
        self.user = make_owner(self.user)
        self.assertEqual(self.user.user_level, "Owner")
        self.user = make_officer(self.user)
        self.assertEqual(self.user.user_level, "Officer")
        self._assert_user_is_valid()

    def test_make_user_a_user_fails(self):
        with self.assertRaises(ValueError):
            self.user = make_user(self.user)

    def test_make_officer_a_user_fails(self):
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        self.user = make_officer(self.user)
        self.assertEqual(self.user.user_level, "Officer")
        with self.assertRaises(ValueError):
            self.user = make_user(self.user)

    def test_make_owner_a_user_fails(self):
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        self.user = make_officer(self.user)
        self.assertEqual(self.user.user_level, "Officer")
        self.user = make_owner(self.user)
        self.assertEqual(self.user.user_level, "Owner")
        with self.assertRaises(ValueError):
            self.user = make_user(self.user)

    def test_make_member_a_member_fails(self):
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        with self.assertRaises(ValueError):
            self.user = make_member(self.user)

    def test_make_owner_a_member_fails(self):
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        self.user = make_officer(self.user)
        self.assertEqual(self.user.user_level, "Officer")
        self.user = make_owner(self.user)
        self.assertEqual(self.user.user_level, "Owner")
        with self.assertRaises(ValueError):
            self.user = make_member(self.user)

    def test_make_user_an_officer_fails(self):
        with self.assertRaises(ValueError):
            self.user = make_officer(self.user)

    def test_make_officer_an_officer_fails(self):
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        self.user = make_officer(self.user)
        self.assertEqual(self.user.user_level, "Officer")
        with self.assertRaises(ValueError):
            self.user = make_officer(self.user)

    def test_make_user_an_owner_fails(self):
        with self.assertRaises(ValueError):
            self.user = make_owner(self.user)

    def test_make_member_an_owner_fails(self):
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        with self.assertRaises(ValueError):
            self.user = make_owner(self.user)

    def test_make_owner_an_owner_fails(self):
        self.user = make_member(self.user)
        self.assertEqual(self.user.user_level, "Member")
        self.user = make_officer(self.user)
        self.assertEqual(self.user.user_level, "Officer")
        self.user = make_owner(self.user)
        self.assertEqual(self.user.user_level, "Owner")
        with self.assertRaises(ValueError):
            self.user = make_owner(self.user)

    def test_promote_applicant_to_member(self):
        self.user.promote()
        self.assertEqual(self.user.user_level, "Member")

    def test_promote_member_to_officer(self):
        self.user = make_member(self.user)
        self.user.promote()
        self.assertEqual(self.user.user_level, "Officer")

    def test_demote_officer_to_member(self):
        self.user = make_member(self.user)
        self.user = make_officer(self.user)
        self.user.demote()
        self.assertEqual(self.user.user_level, "Member")

    def test_promote_officer_fails(self):
        self.user = make_member(self.user)
        self.user = make_officer(self.user)
        with self.assertRaises(ValueError):
            self.user.promote()

    def test_promote_owner_fails(self):
        self.user = make_member(self.user)
        self.user = make_officer(self.user)
        self.user = make_owner(self.user)
        with self.assertRaises(ValueError):
            self.user.promote()

    def test_demote_owner_fails(self):
        self.user = make_member(self.user)
        self.user = make_officer(self.user)
        self.user = make_owner(self.user)
        with self.assertRaises(ValueError):
            self.user.demote()

    def test_demote_member_fails(self):
        self.user = make_member(self.user)
        with self.assertRaises(ValueError):
            self.user.demote()

    def test_demote_applicant_fails(self):
        with self.assertRaises(ValueError):
            self.user.demote()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')
