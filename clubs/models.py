from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from libgravatar import Gravatar


# This user manager is following tutorial from
# https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username/
class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


# The user model was inspired by the one written for clucker.
class User(AbstractUser):
    class ChessExperience(models.TextChoices):
        NEW_TO_CHESS = 'New to chess'
        BEGINNER = 'Beginner'
        INTERMEDIATE = 'Intermediate'
        ADVANCED = 'Advanced'
        EXPERT = 'Expert'

    username = None
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    bio = models.CharField(blank=True, max_length=400)
    chess_exp = models.CharField(choices=ChessExperience.choices, max_length=12)
    personal_statement = models.CharField(blank=True, max_length=500)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

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
    applicants = models.ManyToManyField(User, related_name='not_applicants')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def user_level(self, user):
        if self.owner == user:
            return "Owner"
        elif self.officers.filter(email=user.email):
            return "Officer"
        elif self.members.filter(email=user.email):
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

    def make_applicant(self, user):
        if user not in self.applicants.all():
            self.applicants.add(user)
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
            User.objects.filter(email=self.get_owner().email))

    def get_all_applicants(self):
        return self.applicants.all()

    def get_all_non_applicants(self):
        return User.objects.difference(self.get_all_applicants())


def toggle_superuser(user):
    user.is_staff = not user.is_staff
    user.is_superuser = not user.is_superuser


class ClubApplicationModel(models.Model):
    associated_club = models.ForeignKey(Club, on_delete=models.CASCADE)
    associated_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # wouldn't allow without null = true
