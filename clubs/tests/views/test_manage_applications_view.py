"""Unit tests of the manage application view"""
from django.test import TestCase
from clubs.models import User, Club, ClubApplication, EloRating
from django.urls import reverse
from clubs.tests.views.helpers import reverse_with_next, give_all_missing_elos


class ManageApplicationViewTest(TestCase):
    """Unit tests of the manage application view"""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/other_users.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/other_clubs.json",
        "clubs/tests/fixtures/default_application.json",
        "clubs/tests/fixtures/default_elo.json",
        "clubs/tests/fixtures/other_elo.json"
    ]

    def setUp(self):
        self.url = reverse("manage_applications")
        self.apply_url = reverse("clubs")
        self.first_user = User.objects.get(email="johndoe@example.com")
        self.second_user = User.objects.get(email="janedoe@example.com")
        self.first_club = Club.objects.get(name="Saint Louis Chess Club")
        self.second_club = Club.objects.get(name="Saint Louis Chess Club 2")
        self.first_club_application = ClubApplication.objects.get(associated_club=self.first_club)
        give_all_missing_elos(self.first_club)
        give_all_missing_elos(self.second_club)

    def test_manage_applications_url(self):
        self.assertEqual(self.url, '/manage_applications')

    def test_manage_applications_list(self):
        self.client.login(email=self.first_user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manage_applications.html")
        self.assertEqual(self.first_club_application.associated_user, self.first_user)
        self.assertEqual(self.first_club_application.associated_club, self.first_club)

    def test_manage_applications_list_when_no_applications(self):
        self.first_club_application.delete()
        self.client.login(email=self.first_user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEquals(response.context["applications"], [])

    def test_manage_application_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_submit_creates_application(self):
        self.client.login(email=self.second_user.email, password='Password123')
        temp = Club.objects.count()
        before_count = ClubApplication.objects.count()
        response = self.client.post(self.apply_url, {'name' : self.second_club.name})
        after_count = ClubApplication.objects.count()
        self.assertEqual(after_count, before_count+1)
        self.assertEqual(response.status_code, 200)

    def test_accept_application_deletes_application(self):
        self.client.login(email=self.second_user.email, password='Password123')
        self.client.post(self.apply_url, {'name': self.second_club.name})
        before_count = ClubApplication.objects.count()
        self.client.post(self.url, {'uname': self.second_user.email,
                                    'clubname': self.second_club.name, 'accepted': True})

        after_count = ClubApplication.objects.count()
        self.assertEqual(after_count, before_count - 1)

    def test_reject_application_does_not_delete_application(self):
        self.client.login(email=self.second_user.email, password='Password123')
        self.client.post(self.apply_url, {'name': self.second_club.name})
        before_count = ClubApplication.objects.count()
        self.client.post(self.url, {'uname': self.second_user.email,
                                    'clubname': self.second_club.name, 'rejected': True})

        after_count = ClubApplication.objects.count()
        self.assertEqual(after_count, before_count)

    def test_reject_application_sets_rejected_field_to_true(self):
        self.client.login(email=self.second_user.email, password='Password123')
        self.client.post(self.apply_url, {'name': self.second_club.name})
        c_initial = ClubApplication.objects.get(associated_club=self.second_club, associated_user=self.second_user)
        self.assertFalse(c_initial.is_rejected)
        self.client.post(self.url, {'uname': self.second_user.email,
                                    'clubname': self.second_club.name, 'rejected': True})

        c = ClubApplication.objects.get(associated_club=self.second_club, associated_user=self.second_user)
        self.assertTrue(c.is_rejected)

    def test_single_user_can_submit_multiple_applications(self):
        self.client.login(email=self.second_user.email, password='Password123')
        before_count = ClubApplication.objects.count()
        self.client.post(self.apply_url, {'name': self.first_club.name})
        self.client.post(self.apply_url, {'name': self.second_club.name})
        after_count = ClubApplication.objects.count()
        self.assertEqual(before_count + 2, after_count)

    def test_multiple_applications_can_be_accepted(self):
        self.client.login(email=self.second_user.email, password='Password123')

        self.client.post(self.apply_url, {'name': self.first_club.name})
        self.client.post(self.apply_url, {'name': self.second_club.name})
        before_count = ClubApplication.objects.count()

        self.client.post(self.url, {'uname': self.second_user.email,
                                    'clubname': self.first_club.name, 'accepted': True})
        self.client.post(self.url, {'uname': self.second_user.email,
                                    'clubname': self.second_club.name, 'accepted': True})
        after_count = ClubApplication.objects.count()

        self.assertEqual(before_count - 2, after_count)

    def test_multiple_applications_can_be_rejected(self):
        self.client.login(email=self.second_user.email, password='Password123')
        before_count = ClubApplication.objects.count()
        self.client.post(self.apply_url, {'name': self.first_club.name})
        self.client.post(self.apply_url, {'name': self.second_club.name})
        after_count = ClubApplication.objects.count()
        self.assertEqual(after_count, before_count + 2)

        c1 = ClubApplication.objects.get(associated_club=self.first_club, associated_user=self.second_user)
        c2 = ClubApplication.objects.get(associated_club=self.second_club, associated_user=self.second_user)
        self.assertFalse(c1.is_rejected)
        self.assertFalse(c2.is_rejected)

        before_rejected_count = ClubApplication.objects.count()
        self.client.post(self.url, {'uname': self.second_user.email,
                                    'clubname': self.first_club.name, 'rejected': True})
        self.client.post(self.url, {'uname': self.second_user.email,
                                    'clubname': self.second_club.name, 'rejected': True})

        after_rejected_count = ClubApplication.objects.count()
        self.assertEqual(after_rejected_count, before_rejected_count)

        c1_after_reject = ClubApplication.objects.get(associated_club=self.first_club,
                                                      associated_user=self.second_user)
        c2_after_reject = ClubApplication.objects.get(associated_club=self.second_club,
                                                      associated_user=self.second_user)

        self.assertTrue(c1_after_reject.is_rejected)
        self.assertTrue(c2_after_reject.is_rejected)

    def test_owner_cannot_apply_to_their_club(self):
        self.client.login(email=self.first_user.email, password='Password123')
        before_count = ClubApplication.objects.count()
        temp = self.client.post(self.apply_url, {'name' : self.first_club.name})
        after_count = ClubApplication.objects.count()
        self.assertEqual(before_count, after_count)


    def test_user_cannot_apply_to_their_club(self):
        self.second_club.add_new_member(self.second_user)
        before_count = ClubApplication.objects.count()
        self.client.login(email=self.second_user.email, password='Password123')
        temp = self.client.post(self.apply_url, {'name' : self.second_club.name})
        after_count = ClubApplication.objects.count()
        self.assertEqual(before_count, after_count)



    def test_only_officers_and_owners_can_see_manage_applications_navbar_icon(self):
        self.client.login(email=self.first_user.email, password='Password123')
        # NOTE: this may need to change as the URLs change
        select_club = self.client.get(reverse('users', kwargs={"club_id": self.first_club.id}))
        html_content = str(select_club.content)
        str_to_test = """href="/manage_applications">"""
        res = str_to_test in html_content
        self.assertTrue(res)

    def test_users_can_not_see_manage_applications_navbar_icon(self):
        self.client.login(email=self.second_user.email, password='Password123')
        self.client.post(self.apply_url, {'name': self.second_club.name})
        self.client.post(self.url, {'uname': self.second_user.email,
                                    'clubname': self.second_club.name, 'accepted': True})
        select_club = self.client.get('/2/users')
        html_content = str(select_club.content)
        str_to_test = """href="/manage_applications">"""
        res = str_to_test in html_content
        self.assertFalse(res)

    def test_revert_rejected_applications(self):
        self.client.login(email=self.second_user.email, password='Password123')
        self.client.post(self.apply_url, {'name': self.first_club.name})
        c1 = ClubApplication.objects.get(associated_club=self.first_club, associated_user=self.second_user)
        self.assertFalse(c1.is_rejected)
        before_reverted_count = ClubApplication.objects.count()
        self.client.post(self.url, {'uname': self.second_user.email,'clubname': self.first_club.name, 'rejected': True})
        self.client.post(self.url, {'uname': self.second_user.email,'clubname': self.first_club.name, 'revert': True})
        after_reverted_count = ClubApplication.objects.count()
        # The revert deletes the application, so the user can reapply
        self.assertEqual(before_reverted_count, after_reverted_count+1)
        before_reapply_count = ClubApplication.objects.count()
        self.client.post(self.apply_url, {'name': self.first_club.name})
        after_reapply_count = ClubApplication.objects.count()
        self.assertEqual(before_reapply_count+1, after_reapply_count)
        c2 = ClubApplication.objects.get(associated_club=self.first_club, associated_user=self.second_user)
        self.assertFalse(c2.is_rejected)
