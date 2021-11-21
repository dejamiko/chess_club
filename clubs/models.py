from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from libgravatar import Gravatar


# The user model was inspired by the one written for clucker.
class User(AbstractUser):
    class ChessExperience(models.TextChoices):
        NEW_TO_CHESS = 'New to chess'
        BEGINNER = 'Beginner'
        INTERMEDIATE = 'Intermediate'
        ADVANCED = 'Advanced'
        EXPERT = 'Expert'

    class UserLevel(models.TextChoices):
        APPLICANT = 'Applicant'
        MEMBER = 'Member'
        OFFICER = 'Officer'
        OWNER = 'Owner'

    username = models.CharField(unique=True, max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    bio = models.CharField(blank=True, max_length=400)
    chess_exp = models.CharField(choices=ChessExperience.choices, max_length=12)
    personal_statement = models.CharField(blank=True, max_length=500)
    user_level = models.CharField(choices=UserLevel.choices, max_length=10, default=UserLevel.APPLICANT)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a small version of the user's gravatar."""
        return self.gravatar(size=60)

    def promote(self):
        if self.user_level == "Applicant":
            make_member(self)
        elif self.user_level == "Member":
            make_officer(self)
        else:
            raise ValueError

    def demote(self):
        if self.user_level == "Officer":
            make_member(self)
        else:
            raise ValueError


def make_owner(user):
    if user.user_level == "Officer":
        return change_user_level(user, "Owner")
    else:
        raise ValueError


def make_officer(user):
    if user.user_level == "Member" or user.user_level == "Owner":
        return change_user_level(user, "Officer")
    else:
        raise ValueError


def make_member(user):
    if user.user_level == "Applicant" or user.user_level == "Officer":
        return change_user_level(user, "Member")
    else:
        raise ValueError


def make_user(user):
    if user.user_level == "Member":
        return change_user_level(user, "Applicant")
    else:
        raise ValueError


def change_user_level(user, new_level):
    if user.user_level == "Owner":
        user.is_staff = False
        user.is_superuser = False
        user.is_admin = False
    if new_level == "Owner":
        user.is_staff = True
        user.is_superuser = True
        user.is_admin = True

    user.user_level = new_level
    user.save()

    return user
