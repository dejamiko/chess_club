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

    # On user groups:
    # Django provides the Group and Permission framework, as in you create a group and
    # create permissions for that group and then add users to be in a group (or many groups).
    # The problem is that Permissions are always related to a model in the django application,
    # for instance you might have a permission to create a Post or delete a Post. This doesn't
    # work in our case, as we want to control the flow of other parts of application, unrelated
    # to models.


class Member(User):
    pass


class Officer(User):
    pass


class Owner(User):
    pass


def make_owner(user):
    if type(user) == Officer:
        return change_user_level(user, Owner)
    else:
        raise ValueError


def make_officer(user):
    if type(user) == Member or type(user) == Owner:
        return change_user_level(user, Officer)
    else:
        raise ValueError


def make_member(user):
    if type(user) == User or type(user) == Officer:
        return change_user_level(user, Member)
    else:
        raise ValueError


def make_user(user):
    if type(user) == Member:
        return change_user_level(user, User)
    else:
        raise ValueError


def change_user_level(old_user, new_class):
    data_dict = extract_data(old_user)
    old_user.delete()
    new_user = assign_data(data_dict, new_class)
    new_user.save()
    return new_user


def extract_data(user):
    data_dict = dict(username=user.username,
                     first_name=user.first_name,
                     last_name=user.last_name,
                     email=user.email,
                     password=user.password,
                     bio=user.bio,
                     chess_exp=user.chess_exp,
                     personal_statement=user.personal_statement
                     )
    return data_dict


def assign_data(data_dict, user_class):
    member = user_class.objects.create(
        username=data_dict['username'],
        first_name=data_dict['first_name'],
        last_name=data_dict['last_name'],
        email=data_dict['email'],
        password=data_dict['password'],
        bio=data_dict['bio'],
        chess_exp=data_dict['chess_exp'],
        personal_statement=data_dict['personal_statement']
    )
    return member
