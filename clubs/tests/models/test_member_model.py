from clubs.models import User, make_member
from .test_user_model import UserModelTestCase


class MemberModelTestCase(UserModelTestCase):
    def setUp(self):
        self.user = make_member(User.objects.get(email='johndoe@example.com'))