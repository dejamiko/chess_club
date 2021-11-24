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

    def user_level(self, club):
        return club.user_level(self)

    def promote(self, club):
        if self.user_level(club) == "Applicant":
            club.make_member(self)
        elif self.user_level(club) == "Member":
            club.make_officer(self)
        else:
            raise ValueError

    def demote(self, club):
        if self.user_level(club) == "Officer":
            club.make_member(self)
        else:
            raise ValueError


class Club(models.Model):
    name = models.CharField(unique=True, blank=False, max_length=50)
    location = models.CharField(blank=False, max_length=100)
    description = models.CharField(blank=True, max_length=500)

    members = models.ManyToManyField(User, related_name='not_members')
    officers = models.ManyToManyField(User, related_name='not_officers')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def user_level(self, user):
        if self.owner == user:
            return "Owner"
        elif self.officers.filter(username=user.username):
            return "Officer"
        elif self.members.filter(username=user.username):
            return "Member"
        else:
            return "Applicant"

    def make_owner(self, user):
        if self.user_level(user) == "Officer":
            self.officers.remove(user)
            self.officers.add(self.owner)
            toggle_superuser(self.owner)
            self.owner = user
            toggle_superuser(user)
            self.save()
        else:
            raise ValueError

    def make_officer(self, user):
        if self.user_level(user) == "Member":
            self.members.remove(user)
            self.officers.add(user)
            self.save()
        else:
            raise ValueError

    def make_member(self, user):
        if self.user_level(user) == "Applicant":
            self.members.add(user)
            self.save()
        elif self.user_level(user) == "Officer":
            self.members.add(user)
            self.officers.remove(user)
            self.save()
        else:
            raise ValueError

    def make_user(self, user):
        if self.user_level(user) == "Member":
            self.members.remove(user)
            self.save()
        else:
            raise ValueError

    def get_number_of_members(self):
        return self.members.count()

    def get_number_of_officers(self):
        return self.officers.count()

    def get_members(self):
        return self.members.all()

    def get_officers(self):
        return self.officers.all()

    def get_owner(self):
        return self.owner

    def get_all_users(self):
        return self.get_members().union(self.get_officers()).union(
            User.objects.filter(username=self.get_owner().username))

    def get_all_applicants(self):
        return User.objects.difference(self.get_all_users())


def toggle_superuser(user):
    user.is_staff = not user.is_staff
    user.is_superuser = not user.is_superuser
