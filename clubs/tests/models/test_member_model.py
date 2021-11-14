from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, make_member


class MemberModelTestCase(TestCase):
    fixtures = ['clubs/tests/fixtures/default_user.json', 'clubs/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = make_member(User.objects.get(email='johndoe@example.com'))

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_username_cannot_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def test_username_must_be_unique(self):
        other_user = User.objects.get(email='janedoe@example.com')
        self.user.username = other_user.username
        self._assert_user_is_invalid()

    def test_username_can_be_50_characters_long(self):
        self.user.username = 'x' * 50
        self._assert_user_is_valid()

    def test_username_cannot_be_more_than_50_characters_long(self):
        self.user.username = 'x' * 51
        self._assert_user_is_invalid()

    def test_email_cannot_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        other_user = User.objects.get(email='janedoe@example.com')
        self.user.email = other_user.email
        self._assert_user_is_invalid()

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_does_not_have_to_be_unique(self):
        other_user = User.objects.get(email='janedoe@example.com')
        self.user.first_name = other_user.first_name
        self._assert_user_is_valid()

    def test_first_name_can_be_50_characters_long(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_cannot_be_more_than_50_characters_long(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_does_not_have_to_be_unique(self):
        other_user = User.objects.get(email='janedoe@example.com')
        self.user.last_name = other_user.last_name
        self._assert_user_is_valid()

    def test_last_name_can_be_50_characters_long(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_cannot_be_more_than_50_characters_long(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_emails_must_contain_an_at(self):
        self.user.email = 'johndoeexample.com'
        self._assert_user_is_invalid()

    def test_emails_must_contain_a_dot_in_the_domain(self):
        self.user.email = 'johndoe@examplecom'
        self._assert_user_is_invalid()

    def test_bio_can_be_blank(self):
        self.user.bio = ''
        self._assert_user_is_valid()

    def test_bio_can_be_400_characters_long(self):
        self.user.bio = 'x' * 400
        self._assert_user_is_valid()

    def test_bio_cannot_be_more_than_400_characters_long(self):
        self.user.bio = 'x' * 401
        self._assert_user_is_invalid()

    def test_personal_statement_can_be_blank(self):
        self.user.personal_statement = ''
        self._assert_user_is_valid()

    def test_personal_statement_can_be_500_characters_long(self):
        self.user.personal_statement = 'x' * 500
        self._assert_user_is_valid()

    def test_personal_statement_cannot_be_more_than_500_characters_long(self):
        self.user.personal_statement = 'x' * 501
        self._assert_user_is_invalid()

    def test_chess_exp_cannot_be_blank(self):
        self.user.chess_exp = ''
        self._assert_user_is_invalid()

    def test_chess_exp_can_be_any_of_the_choices(self):
        for level in User.ChessExperience.values:
            self.user.chess_exp = level
            self._assert_user_is_valid()

    def test_chess_exp_can_only_be_one_of_the_choices(self):
        self.user.chess_exp = 'Novice'
        self._assert_user_is_invalid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
