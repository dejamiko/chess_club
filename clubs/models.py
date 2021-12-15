from datetime import datetime
import random

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Model
from django.utils.timezone import make_aware
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default="retro")
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a small version of the user's gravatar."""
        return self.gravatar(size=60)

    def user_level(self, club):
        return club.user_level(self)

    def promote(self, club):
        if self.user_level(club) == "Member":
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

    def get_number_of_tournaments_lost(self):
        counter = 0
        for tournament in self.participates_in.all():
            if tournament.winner and tournament.winner != self:
                counter += 1
        return counter

    def get_highest_elo(self):
        return max(self._get_all_elos())

    def get_lowest_elo(self):
        return min(self._get_all_elos())

    def get_mean_elo(self):
        all_elos = self._get_all_elos()
        return round(sum(all_elos) / len(all_elos), 2)

    def _get_all_elos(self):
        temp_array = []
        for elo in self.user_elo.all():
            temp_array.append(elo.elo_rating)
        return temp_array


class Club(models.Model):
    name = models.CharField(unique=True, blank=False, max_length=50)
    location = models.CharField(blank=False, max_length=100)
    description = models.CharField(blank=True, max_length=500)

    members = models.ManyToManyField(User, related_name='member_of')
    officers = models.ManyToManyField(User, related_name='officer_of')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_of')

    def user_level(self, user):
        if self.owner == user:
            return "Owner"
        elif self.officers.filter(email=user.email):
            return "Officer"
        elif self.members.filter(email=user.email):
            return "Member"

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

    def add_new_member(self, user):
        # Once an application is accepted
        self.members.add(user)
        self.save()

    def make_member(self, user):
        if self.user_level(user) == "Officer":
            self.members.add(user)
            self.officers.remove(user)
            self.save()
        else:
            raise ValueError

    def give_elo(self, user):
        EloRating.objects.create(user=user, club=self, elo_rating=1000)

    def make_user(self, user):
        if self.user_level(user) == "Member":
            self.members.remove(user)
            self.save()
            EloRating.objects.filter(user=user, club=self).delete()
        else:
            raise ValueError

    def get_all_applicants_users(self):
        # This gets all applicants both REJECTED and NOT rejected
        applicant_list = []
        try:
            temp = ClubApplicationModel.objects.filter(associated_club =
            self
            ).all()
        except ClubApplicationModel.DoesNotExist:
            temp = None
        if temp is not None:
            for t in temp:
                applicant_list.append(t.associated_user)
        return applicant_list

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


    def get_all_tournaments(self):
        return self.has_tournaments.all()

    def get_number_of_tournaments(self):
        return self.has_tournaments.count()

    def get_average_elo(self):
        temp_array = []
        for elo in EloRating.objects.filter(club=self):
            temp_array.append(elo.elo_rating)
        return round(sum(temp_array) / len(temp_array), 2)


def toggle_superuser(user):
    user.is_staff = not user.is_staff
    user.is_superuser = not user.is_superuser


class ClubApplicationModel(models.Model):
    associated_club = models.ForeignKey(Club, on_delete=models.CASCADE)
    associated_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # wouldn't allow without null = true
    is_rejected = models.BooleanField(default = False)


class Tournament(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="has_tournaments")
    name = models.CharField(unique=True, blank=False, max_length=50)
    description = models.CharField(blank=True, max_length=500)
    participants = models.ManyToManyField(User, related_name="participates_in")
    organiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organises")
    coorganisers = models.ManyToManyField(User, related_name="coorganises", blank=True)
    deadline = models.DateTimeField(blank=False)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="tournament_wins")
    bye = models.ManyToManyField(User)
    round = models.IntegerField(default=1)
    group_phase = models.BooleanField(default=False)
    elimination_phase = models.BooleanField(default=True)
    is_final = models.BooleanField(default=False)

    SIZE_OF_BRACKET = 16
    NUMBER_OF_GROUPS = int(SIZE_OF_BRACKET / 2)

    def get_number_of_participants(self):
        return self.participants.count()

    def create_initial_pairings(self):
        self.round = 0
        if self.participants.count() > self.SIZE_OF_BRACKET:
            self.create_groups()
            self.group_phase = True
            self.elimination_phase = False
            return self.next_pairings()
        else:
            participants = list(self.participants.all())
            self.round += 1
            return self.create_bracket_pairings(participants)

    def next_pairings(self):
        self.round += 1
        if self.is_final:
            return []

        if self.elimination_phase:
            previous_pairings = self.pairings_within.all().filter(round=self.round - 1)
            players = []
            for pairing in previous_pairings:
                match = Match.objects.get(pairing=pairing)
                players.append(match.winner)
            players = players + list(self.bye.all())
            self.bye.set([])

            return self.create_bracket_pairings(players)

        pairings = []
        if self.group_phase:
            for group in self.groups_within.all():
                self.group_phase = False
                new_pairings = group.get_next_pairings()
                if new_pairings is not None:
                    pairings += new_pairings
                    self.group_phase = True
            if len(pairings) > 0:
                return pairings

        self.elimination_phase = True
        players = []
        for group in self.groups_within.all():
            players += group.get_top_seeds()
        ordering = []
        for i in range(0, self.NUMBER_OF_GROUPS):
            ordering.append((players[2 * i], players[self.SIZE_OF_BRACKET - 1 - 2 * i]))
        pairings = self.create_bracket_pairings(players, ordering=ordering)
        return pairings

    def create_groups(self):
        participant_list = list(self.participants.all())
        for i in range(0, self.NUMBER_OF_GROUPS):
            group = Group.objects.create(
                tournament=self,
                group_number=i
            )
            group.save()

        # This method is more evenly spread than just taking the first however many users
        # because the last group could be way smaller. Here the difference is at most 1
        for i in range(0, len(participant_list)):
            group = self.groups_within.get(group_number=i % self.NUMBER_OF_GROUPS, tournament=self)
            group.participants.add(participant_list[i])
            group.save()

    def create_bracket_pairings(self, participants, ordering=None):
        self.is_final = False
        if len(participants) % 2 == 1:
            self.bye.add(participants[-1])
            participants = participants[0: len(participants) - 1]

        if ordering is None:
            ordering = []
            for i in range(0, len(participants), 2):
                ordering.append((participants[i], participants[i + 1]))

        pairings = []
        for pair in ordering:
            if pair[1] is not None and pair[0] is not None:
                pairing = Pairing.objects.create(
                    tournament=self,
                    white_player=pair[0],
                    black_player=pair[1],
                    round=self.round
                )
                pairing.save()
                pairings.append(pairing)

        if len(pairings) == 1 and self.bye.count() == 0:
            self.is_final = True

        self.save()

        return pairings

    def get_all_matches(self):
        return list(Match.objects.filter(pairing__in=self.pairings_within.all()))

    def all_pairings_completed(self):
        if self.pairings_within.count() > 0:
            for pairing in self.pairings_within.all():
                if not pairing.match_exists():
                    return False
            return True
        else:
            return False

    def set_winner(self, winner):
        self.winner = winner

    def make_participant(self, user):
        if user not in self.participants.all():
            self.participants.add(user)
            self.save()
        else:
            raise ValueError

    def remove_participant(self, user):
        if user in self.participants.all():
            self.participants.remove(user)
            self.save()
        else:
            raise ValueError

    def get_all_participants(self):
        return self.participants.all()

    def get_status(self):
        if self.winner:
            return "Completed"
        elif self.deadline < make_aware(datetime.now()):
            return f"Round {self.round}"
        elif self.participants.count() > 95:
            return "Applications full"
        else:
            return "Taking applications"

class Pairing(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="pairings_within")
    white_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plays_white_in")
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plays_black_in")

    round = models.IntegerField(blank=False)

    def get_other_player(self, player):
        if player == self.white_player:
            return self.black_player
        else:
            return self.white_player

    def match_exists(self):
        return Match.objects.filter(pairing=self)


def pairing_to_match_elimination_phase(pairing, winner=None):
    if winner:
        win_scenario = Match.objects.create(
            pairing=pairing,
            winner=winner,
            loser=pairing.get_other_player(winner),
            is_draw=False
        )
        win_scenario.set_winner()
        win_scenario.save()
        return win_scenario
    else:
        # A simplified view - if the match is a draw, the arbiter flips a coin
        if random.randint(0, 1) > 0:
            draw_scenario = Match.objects.create(
                pairing=pairing,
                winner=pairing.white_player,
                loser=pairing.black_player,
                is_draw=True
            )
            draw_scenario.set_draw()
            draw_scenario.save()
            return draw_scenario
        else:
            draw_scenario = Match.objects.create(
                pairing=pairing,
                winner=pairing.black_player,
                loser=pairing.white_player,
                is_draw=True
            )
            draw_scenario.set_draw()
            draw_scenario.save()
            return draw_scenario


def pairing_to_match_group_phase(pairing, winner=None):
    if winner:
        win_scenario = Match.objects.create(
            pairing=pairing,
            winner=winner,
            loser=pairing.get_other_player(winner),
            is_draw=False
        )
        win_scenario.set_winner()
        win_scenario.save()
        return win_scenario

    else:
        draw_scenario = Match.objects.create(
            pairing=pairing,
            is_draw=True
        )
        draw_scenario.set_draw()
        draw_scenario.save()
        return draw_scenario


class EloRating(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="has_elo_club")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_elo')
    elo_rating = models.IntegerField()

    def assign_elo(self, club, user, elo_rating):
        self.club = club
        self.user = user
        self.elo_rating = elo_rating


class Group(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="groups_within")
    participants = models.ManyToManyField(User, related_name="participant_in_group")
    group_number = models.IntegerField(blank=False)
    pairings = models.ManyToManyField(Pairing, related_name="group_in_which_the_paring_takes_place")

    def create_all_pairs(self):
        # Create the whole table of pairings for the group.
        # I'm using the Berger algorithm as described here
        # https://en.wikipedia.org/wiki/Round-robin_tournament#Scheduling_algorithm
        # I allocate each participant a number, corresponding to the index in the
        # participants field + 1
        self.player_list = list(self.participants.all())
        participant_numbers = list(range(1, len(self.player_list) + 1))
        if len(participant_numbers) % 2 == 1:
            # we need to add a dummy participant
            participant_numbers.append(len(participant_numbers) + 1)

        n = len(participant_numbers)

        pairs = [[]]
        for i in range(0, int(n / 2)):
            pairs[0].append((participant_numbers[i], participant_numbers[n - 1 - i]))

        for i in range(1, n - 1):
            new_row = []
            for j in range(0, len(pairs[i - 1])):
                first_num = pairs[i - 1][j][0]
                second_num = pairs[i - 1][j][1]

                if first_num == n:
                    new_first_num = (second_num + n / 2)
                    new_second_num = n
                    if new_first_num > n - 1:
                        new_first_num -= n - 1
                elif second_num == n:
                    new_first_num = n
                    new_second_num = (first_num + n / 2)
                    if new_second_num > n - 1:
                        new_second_num -= n - 1
                else:
                    new_first_num = (first_num + n / 2)
                    new_second_num = (second_num + n / 2)
                    if new_first_num > n - 1:
                        new_first_num -= n - 1
                    if new_second_num > n - 1:
                        new_second_num -= n - 1

                new_row.append((int(new_first_num), int(new_second_num)))
            pairs.append(new_row)

        for i in range(0, len(pairs)):
            for pair in pairs[i]:
                if len(self.player_list) % 2 == 0 or (pair[0] != n and pair[1] != n):
                    pairing = Pairing.objects.create(
                        tournament=self.tournament,
                        white_player=self.player_list[pair[0] - 1],
                        black_player=self.player_list[pair[1] - 1],
                        round=i + 1
                    )
                    self.pairings.add(pairing)
                    pairing.save()

        return list(pairs)

    def get_next_pairings(self):
        if self.pairings.count() == 0:
            self.create_all_pairs()
        if self.tournament.round > self.participants.count():
            return None
        return self.pairings.filter(round=self.tournament.round)

    def get_ranking(self):
        players_and_points = {}
        for player in self.participants.all():
            players_and_points[player] = 0
        for pairing in self.pairings.all():
            match = Match.objects.get(pairing=pairing)
            if match.is_draw:
                players_and_points[pairing.white_player] += 0.5
                players_and_points[pairing.black_player] += 0.5
            else:
                players_and_points[match.winner] += 1

        return players_and_points

    def get_top_seeds(self):
        ranking = self.get_ranking()
        max_score = 0
        first_seed = list(self.participants.all())[0]
        second_seed = list(self.participants.all())[1]
        for (player, score) in ranking.items():
            if score > max_score:
                max_score = score
                first_seed = player
        max_score = 0
        for (player, score) in ranking.items():
            if score > max_score and player != first_seed:
                max_score = score
                second_seed = player

        return [first_seed, second_seed]


class Match(models.Model):
    pairing = models.ForeignKey(Pairing, blank=False, on_delete=models.CASCADE, related_name="match")
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="match_wins")
    loser = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="match_losses")
    is_draw = models.BooleanField(blank=True)

    def set_winner(self):

        winner_new_rating = self.set_elo_winner(self.winner, self.loser)
        loser_new_rating = self.set_elo_loser(self.winner, self.loser)

        w_user = User.objects.get(email=self.winner.email)
        l_user = User.objects.get(email=self.loser.email)
        m_club = Club.objects.get(id=self.pairing.tournament.club.id)

        w_elo = EloRating.objects.get(user=w_user, club=m_club)
        w_elo.elo_rating = winner_new_rating
        w_elo.save()

        l_elo = EloRating.objects.get(user=l_user, club=m_club)
        l_elo.elo_rating = loser_new_rating
        l_elo.save()

    def set_draw(self):
        user_draw_black = self.pairing.black_player
        user_draw_white = self.pairing.white_player

        black_new_rating = self.set_elo_draw_black(user_draw_white,user_draw_black)
        white_new_rating = self.set_elo_draw_white(user_draw_white, user_draw_black)

        b_user = User.objects.get(email=self.pairing.black_player.email)
        wh_user = User.objects.get(email=self.pairing.white_player.email)
        m_club = Club.objects.get(id=self.pairing.tournament.club.id)

        b_elo = EloRating.objects.get(user=b_user, club=m_club)
        b_elo.elo_rating = black_new_rating
        b_elo.save()

        wh_elo = EloRating.objects.get(user=wh_user, club=m_club)
        wh_elo.elo_rating = white_new_rating
        wh_elo.save()

    def get_elo_player(self, player):
        t_user = User.objects.get(email=player.email)
        m_club = Club.objects.get(id=self.pairing.tournament.club.id)
        t_elo = EloRating.objects.get(user=t_user, club=m_club)
        return t_elo.elo_rating

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
