"""Unit tests of the create club view"""
from django.test import TestCase
from clubs.forms import CreateClubForm
from django.urls import reverse
from clubs.models import User, Club
from clubs.tests.views.helpers import reverse_with_next


class CreateClubViewTestCase(TestCase):
    """Unit tests of the create club view"""

    fixtures = ["clubs/tests/fixtures/default_user.json"]

    def setUp(self):
        self.url = reverse('create_club')
        self.user = User.objects.get(email='johndoe@example.com')
        self.form_input = {
            'name': 'some club',
            'location': 'KCL',
            'description': 'short description here',
            'owner': self.user
        }

    def test_create_club_url(self):
        self.assertEqual(self.url, '/create_club')

    def test_get_create_club(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertFalse(form.is_bound)

    # Change once drop down is done
    # def test_get_create_club_redirect_when_form_completed(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     response = self.client.get(self.url, follow=True)
    #     redirect_url = reverse('home_page')
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'home_page.html')

    def test_unsuccesful_create_club(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = Club.objects.count()
        self.form_input['name'] = ''
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertTrue(form.is_bound)

    def test_successful_create_club(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = Club.objects.count()
        CreateClubForm(data=self.form_input)
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        # change once drop down done
        response_url = reverse("club_page", kwargs={"club_id": 1})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        club = Club.objects.get(name='some club')
        self.assertEqual(club.name, 'some club')
        self.assertEqual(club.location, 'KCL')
        self.assertEqual(club.description, 'short description here')

    def test_club_page_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
