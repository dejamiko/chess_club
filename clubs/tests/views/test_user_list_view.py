"""Unit tests of the user list view"""
from django.test import TestCase
from django.urls import reverse
from clubs.tests.views.helpers import reverse_with_next
from clubs.models import User, Club, EloRating


class UserListTest(TestCase):
    """Unit tests of the user list view"""
    fixtures = ["clubs/tests/fixtures/default_user.json", 'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json', "clubs/tests/fixtures/other_clubs.json",
                "clubs/tests/fixtures/default_elo.json", "clubs/tests/fixtures/other_elo.json"]

    def setUp(self):
        EloRating.objects.filter(pk=2).delete()
        EloRating.objects.filter(pk=3).delete()
        self.user = User.objects.get(email='janedoe@example.com')
        self.bob = User.objects.get(email='bobdoe@example.com')
        self.club = Club.objects.get(name='Saint Louis Chess Club')
        self.url = reverse("users", kwargs={'club_id': self.club.id})

    def test_user_list_url(self):
        self.assertEqual(self.url, "/1/users")

    def test_logged_in_redirect(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_applicant_cannot_access_list(self):
        self.club.make_applicant(self.user)
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, "no_access_screen.html")

    def test_member_can_only_see_members(self):
        self.club.make_member(self.user)

        self._create_test_users(start_id=5, count=5)
        self._create_test_users(start_id=10, count=5, level="Member")
        self._create_test_users(start_id=15, count=5, level="Officer")
        self._create_test_users(start_id=20, count=1, level="Owner")

        response = self._access_user_list_page()
        self.assertEqual(len(response.context["users"]), self.club.get_number_of_members())

        for user_id in range(5, 10):
            self.assertNotContains(response, f"First {user_id} Last {user_id}")

        for user_id in range(10, 15):
            self.assertContains(response, f"First {user_id} Last {user_id}")

        for user_id in range(15, 21):
            self.assertNotContains(response, f"First {user_id} Last {user_id}")

    def test_member_sees_limited_variables(self):
        self.club.make_member(self.user)

        response = self._access_user_list_page()
        self.assertContains(response, "Name")
        self.assertContains(response, "Chess experience")
        self.assertNotContains(response, "Email")
        self.assertNotContains(response, "Role")
        self.assertNotContains(response, "Options")

    def test_officer_can_see_everyone(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)

        self._create_test_users(start_id=5, count=5)
        self._create_test_users(start_id=10, count=5, level="Member")
        self._create_test_users(start_id=15, count=5, level="Officer")
        self._create_test_users(start_id=20, count=1, level="Owner")

        response = self._access_user_list_page()
        self.assertEqual(len(response.context["users"]), self.club.get_all_users().count())

        for user_id in range(10, 21):
            self.assertContains(response, f"First {user_id} Last {user_id}")
            self.assertContains(response, f"{user_id}@test.com")

    def test_officer_sees_all_variables(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)

        response = self._access_user_list_page()
        self.assertContains(response, "Name")
        self.assertContains(response, "Chess experience")
        self.assertContains(response, "Email")
        self.assertContains(response, "Role")
        self.assertContains(response, "Options")

    def test_owner_can_see_everyone(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)

        self._create_test_users(start_id=5, count=5)
        self._create_test_users(start_id=10, count=5, level="Member")
        self._create_test_users(start_id=15, count=5, level="Officer")
        self._create_test_users(start_id=20, count=1, level="Owner")

        response = self._access_user_list_page()
        self.assertEqual(len(response.context["users"]), self.club.get_all_users().count())

        for user_id in range(10, 21):
            self.assertContains(response, f"First {user_id} Last {user_id}")
            self.assertContains(response, f"{user_id}@test.com")

    def test_owner_sees_all_variables(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)

        response = self._access_user_list_page()
        self.assertContains(response, "Name")
        self.assertContains(response, "Chess experience")
        self.assertContains(response, "Email")
        self.assertContains(response, "Role")
        self.assertContains(response, "Options")

    def test_officer_has_promote_button_for_member(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)

        self._create_test_users(start_id=0, count=1, level="Member")

        response = self._access_user_list_page()
        self.assertContains(response, "Promote")

    def test_officer_has_no_promote_button_for_officer(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)

        self._create_test_users(start_id=0, count=1, level="Officer")

        response = self._access_user_list_page()
        self.assertNotContains(response, "Promote")

    def test_officer_has_no_promote_button_for_owner(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)

        self._create_test_users(start_id=0, count=1, level="Owner")

        response = self._access_user_list_page()
        self.assertNotContains(response, "Promote")

    def test_owner_has_no_promote_button_for_officer(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)

        self._create_test_users(start_id=0, count=1, level="Officer")

        response = self._access_user_list_page()
        self.assertNotContains(response, "Promote")

    def test_owner_has_demote_button_for_officer(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)

        self._create_test_users(start_id=0, count=1, level="Officer")

        response = self._access_user_list_page()
        self.assertContains(response, "Demote")

    def test_owner_has_switch_ownership_button_for_officer(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)

        self._create_test_users(start_id=0, count=1, level="Officer")

        response = self._access_user_list_page()
        self.assertContains(response, "Switch ownership")
    
    def test_promote_button(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_member(self.bob)

        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, {"listed_user": self.bob.email, "promote": "Promote"}, follow=True)
        self.assertContains(response, "Bob Doe was promoted to officer!")
        self.assertEqual(self.club.user_level(self.bob), "Officer")
    
    def test_demote_button(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_member(self.bob)
        self.club.make_officer(self.bob)

        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, {"listed_user": self.bob.email, "demote": "Demote"}, follow=True)
        self.assertContains(response, "Bob Doe was demoted to member!")
        self.assertEqual(self.club.user_level(self.bob), "Member")
    
    def test_switch_ownership_button(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)
        self.club.make_member(self.bob)
        self.club.make_officer(self.bob)

        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, {"listed_user": self.bob.email, "switch_owner": "Switch ownership"}, follow=True)
        self.assertContains(response, "You switched ownership with Bob Doe!")
        self.assertEqual(Club.objects.get(name="Saint Louis Chess Club").user_level(self.bob), "Owner")

    def _access_user_list_page(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_list.html")
        return response

    def _create_test_users(self, start_id=0, count=5, level="Applicant"):
        for user_id in range(start_id, start_id + count):
            temp_user = User.objects.create_user(
                id=user_id,
                first_name=f"First {user_id}",
                last_name=f"Last {user_id}",
                email=f"{user_id}@test.com",
                chess_exp="Beginner",
            )
            if level == "Owner":
                self.club.make_member(temp_user)
                self.club.make_officer(temp_user)
                self.club.make_owner(temp_user)
            if level == "Officer":
                self.club.make_member(temp_user)
                self.club.make_officer(temp_user)
            if level == "Member":
                self.club.make_member(temp_user)
