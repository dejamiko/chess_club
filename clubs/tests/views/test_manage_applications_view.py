"""Unit tests of the manage application view"""
from django.test import TestCase
from clubs.models import User, Club, ClubApplicationModel
from django.urls import reverse
from clubs.tests.views.helpers import reverse_with_next


class ManageApplicationViewTest(TestCase):
    """Unit tests of the manage application view"""
    fixtures = [
        "clubs/tests/fixtures/default_user.json",
        "clubs/tests/fixtures/other_users.json",
        "clubs/tests/fixtures/default_club.json",
        "clubs/tests/fixtures/other_clubs.json",
        "clubs/tests/fixtures/default_application.json",
        #"clubs/tests/fixtures/other_application.json",
    ]

    def setUp(self):
        self.url = reverse("manage_applications")
        self.apply_url = reverse("clubs")
        self.first_user = User.objects.get(email="johndoe@example.com")
        self.second_user = User.objects.get(email="janedoe@example.com")
        self.first_club = Club.objects.get(name="Saint Louis Chess Club")
        self.second_club = Club.objects.get(name="Saint Louis Chess Club 2")
        self.first_club_application = ClubApplicationModel.objects.get(associated_club=self.first_club)
        #self.second_club_application = ClubApplicationModel.objects.get(associated_club=self.second_club)

    def test_manage_applications_url(self):
        self.assertEqual(self.url, '/home/clubs/manage_applications/')

    def test_manage_applications_list(self):
        self.client.login(email=self.first_user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manage_applications.html")
        self.assertEqual(self.first_club_application.associated_user, self.first_user)
        self.assertEqual(self.first_club_application.associated_club, self.first_club)
        #self.assertEqual(self.second_club_application.associated_user, self.second_user)
        #self.assertEqual(self.second_club_application.associated_club, self.second_club)

    def test_manage_application_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)


    def test_submit_creates_application(self):
        self.client.login(email=self.first_user.email, password='Password123')
        temp = Club.objects.count()
        before_count = ClubApplicationModel.objects.count()
        response = self.client.post(self.apply_url, {'name' : self.second_club.name})
        after_count = ClubApplicationModel.objects.count()
        self.assertEqual(after_count, before_count+1)
        self.assertEqual(response.status_code, 200)


    # def test_submit_passes_correct_data(self):
    #     self.client.login(email=self.first_user.email, password='Password123')
    #     response = self.client.post(self.apply_url, {'name' : self.second_club.name})
    #     temp = response.get('obj', '')
    #     print("aaaaaaaaaaaaaaaaaaaaa" + str(temp) + "bbbbbbbbbbbbbbb")

    def test_accept_application_deletes_application(self):
        self.client.login(email=self.first_user.email, password='Password123')
        temp = self.client.post(self.apply_url, {'name' : self.second_club.name})
        # temp = Club.objects.count()
        # before_count = ClubApplicationModel.objects.count()
        response = self.client.post(self.url, {'uname' : self.first_user.email,
        'clubname': self.second_club.name,
        'accepted': True
        })
        #
        # after_count = ClubApplicationModel.objects.count()
        # self.assertEqual(after_count, before_count-1)
        # self.assertEqual(response.status_code, 200)

    def test_reject_application_sets_rejected(self):
        pass

    def test_reject_pass_correct_data(self):
        pass

    def test_user_can_submit_multiple_applications(self):
        pass
