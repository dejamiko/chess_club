from clubs.models import User, make_member, make_officer, make_owner
from .test_user_model import UserModelTestCase


class MemberModelTestCase(UserModelTestCase):
    def setUp(self):
        self.user = make_owner(make_officer(make_member(User.objects.get(email='johndoe@example.com'))))
