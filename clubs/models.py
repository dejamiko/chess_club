from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from libgravatar import Gravatar
import math


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
    elo_rating = models.IntegerField(default=1000)

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

    def get_number_of_matches_played(self):
        return self.plays_white_in.count() + self.plays_black_in.count()

    def get_number_of_matches_won(self):
        return self.match_wins.count()

    def get_number_of_matches_lost(self):
        return self.match_losses.count()

    def get_number_of_tournaments_won(self):
        return self.tournament_wins.count()

    def get_number_of_tournaments_participated_in(self):
        return self.participates_in.count()


class Club(models.Model):
    name = models.CharField(unique=True, blank=False, max_length=50)
    location = models.CharField(blank=False, max_length=100)
    description = models.CharField(blank=True, max_length=500)

    members = models.ManyToManyField(User, related_name='member_of')
    officers = models.ManyToManyField(User, related_name='officer_of')
    applicants = models.ManyToManyField(User, related_name='applicant_of')
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

    def get_all_tournaments(self):
        return self.has_tournaments.all()

    def get_number_of_tournaments(self):
        return self.has_tournaments.count()


def toggle_superuser(user):
    user.is_staff = not user.is_staff
    user.is_superuser = not user.is_superuser


class ClubApplicationModel(models.Model):
    associated_club = models.ForeignKey(Club, on_delete=models.CASCADE)
    associated_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # wouldn't allow without null = true


class Tournament(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="has_tournaments")
    name = models.CharField(unique=True, blank=False, max_length=50)
    description = models.CharField(blank=True, max_length=500)
    participants = models.ManyToManyField(User, related_name="participates_in")
    organiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organises")
    coorganisers = models.ManyToManyField(User, related_name="coorganises")
    deadline = models.DateTimeField(blank=False)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="tournament_wins")

    def get_number_of_participants(self):
        return self.participants.count()

    def get_all_matches(self):
        return self.matches_within.all()


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="matches_within")
    white_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plays_white_in")
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plays_black_in")
    winner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="match_wins")
    loser = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="match_losses")

    def set_winner(self, winner_user):
        self.winner = winner_user

        if self.white_player == winner_user:
            self.loser = self.black_player
            loser_user = self.loser

            winner_new_rating = self.set_elo_winner(winner_user, loser_user)
            loser_new_rating = self.set_elo_loser(winner_user, loser_user)
        else:
            self.loser = self.white_player
            loser_user = self.loser

            winner_new_rating = self.set_elo_winner(winner_user, loser_user)
            loser_new_rating = self.set_elo_loser(winner_user, loser_user)

        winner_user.elo_rating = winner_new_rating
        loser_user.elo_rating = loser_new_rating

        self.loser.save()
        self.winner.save()

    def set_draw(self):
        user_draw_black = self.black_player
        user_draw_white = self.white_player

        black_new_rating = self.set_elo_draw_black(user_draw_white,user_draw_black)
        white_new_rating = self.set_elo_draw_white(user_draw_white, user_draw_black)

        user_draw_black.elo_rating = black_new_rating
        user_draw_white.elo_rating = white_new_rating

        self.black_player.save()
        self.white_player.save()


    def get_elo_player(self, player):
        return player.elo_rating

    def expected_outcome(self, winner_user, loser_user):
        current_elo_winner = self.get_elo_player(winner_user)
        current_elo_loser = self.get_elo_player(loser_user)
        exponent_calc = (current_elo_loser - current_elo_winner) / 400
        expected_outcome = 1 / (1 + pow(10, exponent_calc))
        return expected_outcome

    def expected_outcome_alt(self, winner_user, loser_user):
        expected_outcome = 1 - self.expected_outcome(winner_user, loser_user)
        return expected_outcome

    def set_elo_winner(self, winner_user, loser_user):
        winner_current_elo = self.get_elo_player(winner_user)
        expected_outcome_winner = self.expected_outcome(winner_user, loser_user)
        winner_new_elo = winner_current_elo + 32 * (1 - expected_outcome_winner)
        return winner_new_elo

    def set_elo_loser(self, winner_user, loser_user):
        loser_current_elo = self.get_elo_player(loser_user)
        expected_outcome_loser = self.expected_outcome_alt(winner_user, loser_user)
        loser_new_elo = loser_current_elo + 32 * (0 - expected_outcome_loser)
        return loser_new_elo


    def set_elo_draw_white(self, white_player, black_player):
        white_current_elo = self.get_elo_player(white_player)
        white_expected_outcome = self.expected_outcome(white_player, black_player)
        white_new_elo = white_current_elo + 32 * (0.5 - white_expected_outcome)
        return white_new_elo

    def set_elo_draw_black(self, white_player, black_player):
        black_current_elo = self.get_elo_player(black_player)
        black_expected_outcome = self.expected_outcome_alt(white_player, black_player)
        black_new_elo = black_current_elo + 32 * (0.5 - black_expected_outcome)
        return black_new_elo
