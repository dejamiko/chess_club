"""Unit tests of the user manager model."""
from django.test import TestCase
from clubs.models import User


class UserManagerModelTestCase(TestCase):
    """Unit tests of the user manager model."""

    def test_create_superuser(self):
        superuser = User.objects.create_superuser("johndoe@example.com", "Password123")
        self.assertTrue(superuser.is_staff, True)
        self.assertTrue(superuser.is_superuser, True)
    
    def test_create_superuser_without_is_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser("johndoe@example.com", "Password123", is_staff=False)
    
    def test_create_superuser_without_is_superuser(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser("johndoe@example.com", "Password123", is_superuser=False)

    def test_create_user_with_no_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user("", "Password123")