"""Unit tests of the log out view"""
from django.test import TestCase
from clubs.models import User
from django.urls import reverse
from .helpers import LogInTester, reverse_with_next


class LogOutViewTestCase(TestCase, LogInTester):
    """Unit tests of the log out view"""
    fixtures = ["clubs/tests/fixtures/default_user.json"]

    def setUp(self):
        self.url = reverse("log_out")
        self.user = User.objects.get(email="johndoe@example.com")

    def test_redirect_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url,
                             status_code=302, target_status_code=200)

    def test_log_out_url(self):
        self.assertEqual(self.url, '/log_out')

    def test_get_log_out(self):
        self.client.login(email=self.user.email, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('welcome_screen')
        self.assertRedirects(response, response_url,
                             status_code=302, target_status_code=200)
        template_dict = {'welcome_screen.html', 'base.html', 'partials/background.html'}
        for t in template_dict:
            self.assertTemplateUsed(response, t)
        self.assertFalse(self._is_logged_in())
