from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from libgravatar import Gravatar


class User(AbstractUser):

    class ChessExperience(models.TextChoices):
        NEW_TO_CHESS = 'New to chess'
        BEGINNER = 'Beginner'
        INTERMEDIATE = 'Intermediate'
        ADVANCED = 'Advanced'
        EXPERT = 'Expert'

    username = models.CharField(unique=True, max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    bio = models.CharField(blank=True, max_length=400)
    chess_exp = models.CharField(choices=ChessExperience.choices, max_length=12)
    personal_statement = models.CharField(blank=True, max_length=500)

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
