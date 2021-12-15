import math
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils.timezone import make_aware
from faker import Faker
from clubs.models import User, Club, Tournament, pairing_to_match_elimination_phase, pairing_to_match_group_phase, \
    EloRating
import random


def create_set_users():
    User.objects.create(
        first_name='Jebediah',
        last_name='Kerman',
        email='jeb@example.org',
        bio='Hi, I am Jeb',
        chess_exp='Beginner',
        personal_statement='I like chess a lot!',
        password="pbkdf2_sha256$260000$VEDi9wsMYG6eNVeL8WSPqj$LHEiR2iUkusHCIeiQdWS+xQGC9/CjhhrjEOESMMp+c0=",
    )
    User.objects.create(
        first_name='Valentina',
        last_name='Kerman',
        email='val@example.org',
        bio='Hi, I am Val',
        chess_exp='Advanced',
        personal_statement='Chess is a game of infinite beauty',
        password="pbkdf2_sha256$260000$VEDi9wsMYG6eNVeL8WSPqj$LHEiR2iUkusHCIeiQdWS+xQGC9/CjhhrjEOESMMp+c0=",
    )
    User.objects.create(
        first_name='Billie',
        last_name='Kerman',
        email='billie@example.org',
        bio='Hi, I am Billie',
        chess_exp='Intermediate',
        personal_statement='64 squares and billions of possibilities!',
        password="pbkdf2_sha256$260000$VEDi9wsMYG6eNVeL8WSPqj$LHEiR2iUkusHCIeiQdWS+xQGC9/CjhhrjEOESMMp+c0=",
    )


def generate_tournament_matches(tournament, number_of_rounds=0, finish=False):
    while (not tournament.winner) and (finish or tournament.round <= number_of_rounds):
        if tournament.pairings_within.count() == 0:
            pairings = tournament.create_initial_pairings()
        else:
            pairings = tournament.next_pairings()
        for pairing in pairings:
            # The chance of draws is highest for the best players
            # I arbitrarily chose 3000 elo as the elo where all games are draws
            # (which is not true for computer engines)
            tournament_club = tournament.club
            temp_white_player = User.objects.get(id=pairing.white_player.id)
            temp_black_player = User.objects.get(id=pairing.black_player.id)
            elo_white = EloRating.objects.get(user=temp_white_player, club=tournament_club)
            elo_black = EloRating.objects.get(user=temp_black_player, club=tournament_club)
            r_a = elo_white.elo_rating
            r_b = elo_black.elo_rating
            is_draw = (r_a + r_b) / 6000  # average elo divided by 3000

            if random.random() < is_draw:
                if tournament.group_phase:
                    match = pairing_to_match_group_phase(pairing)
                else:
                    match = pairing_to_match_elimination_phase(pairing)
            else:
                e_a = 1 / (1 + pow(10, (r_b - r_a) / 400.0))
                if random.random() < e_a:
                    if tournament.group_phase:
                        match = pairing_to_match_group_phase(pairing, pairing.white_player)
                    else:
                        match = pairing_to_match_group_phase(pairing, pairing.white_player)
                else:
                    if tournament.group_phase:
                        match = pairing_to_match_group_phase(pairing, pairing.black_player)
                    else:
                        match = pairing_to_match_group_phase(pairing, pairing.black_player)

            match.save()

            if tournament.is_final and tournament.all_pairings_completed():
                tournament.set_winner(match.winner)
                tournament.save()


def get_user():
    return list(User.objects.all())[random.randint(0, User.objects.count() - 1)]


def get_club():
    return list(Club.objects.all())[random.randint(0, Club.objects.count() - 1)]


def get_number_of_applicants(club, number):
    possible = list(User.objects.all().difference(club.get_all_users()))
    random.shuffle(possible)
    return possible[0: number]


def create_user_experience():
    xp_levels = ['New to chess', 'Beginner', 'Intermediate', 'Advanced', 'Expert']
    xp_chooser = random.randint(0, 4)
    return xp_levels[xp_chooser]


def create_email(first_name, last_name):
    email = f'{first_name.lower()}.{last_name.lower()}@fakerseed.org'
    return email


def create_future_tournament(club):
    members = list(club.members.all())
    random.shuffle(members)
    participants = members[0: random.randint(4, len(members))]
    coorganisers = members[0: random.randint(0, 5)]

    jeb = User.objects.get(email='jeb@example.org')
    val = User.objects.get(email='val@example.org')

    if jeb in participants:
        participants.remove(jeb)

    if jeb in coorganisers:
        coorganisers.remove(jeb)

    future_tournament = Tournament.objects.create(
        club=club,
        name='Space Tournament',
        organiser=val,
        description='Chess but also space, what else could you possibly need?',
        deadline=make_aware(datetime.now() + timedelta(hours=24))
    )

    future_tournament.participants.set(participants)
    future_tournament.coorganisers.set(coorganisers)

    future_tournament.save()


def create_current_tournament(club):
    members = list(club.members.all())
    random.shuffle(members)
    participants = members[0: random.randint(4, len(members))]
    coorganisers = members[0: random.randint(0, 5)]

    jeb = User.objects.get(email='jeb@example.org')
    val = User.objects.get(email='val@example.org')

    if jeb not in participants:
        participants.append(jeb)

    current_tournament = Tournament.objects.create(
        club=club,
        name='Space Tournament but better',
        organiser=val,
        description='Come on, chess is not rocket science!',
        deadline=make_aware(datetime.now() - timedelta(hours=24))
    )
    current_tournament.participants.set(participants)
    current_tournament.coorganisers.set(coorganisers)

    current_tournament.save()


class Command(BaseCommand):
    """The database seeder."""

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')
        self.max_user_number = 500
        self.number_of_members = 60
        self.number_of_officers = 10
        self.max_club_number = 20
        self.max_tournament_number = 15
        self.max_tournament_number_for_kerbal = 3

    def handle(self, *args, **options):
        self.generate_users()
        self.generate_clubs()
        self.generate_tournaments()

    def generate_users(self):
        user_counter = 0
        create_set_users()
        print("Set users created")
        while user_counter < self.max_user_number:
            try:
                self.create_user()
                user_counter += 1
                print(f'{user_counter}/{self.max_user_number} user has been created', end='\r')
            except IntegrityError:
                print("This email was already taken")
        print('User seeding has been completed successfully')

    def generate_clubs(self):
        club_counter = 0
        self.create_set_clubs()
        print("Set clubs created", end='\r')
        while club_counter < self.max_club_number:
            try:
                club = self.create_club()
                club.full_clean()
                self.generate_club_users(club)
                club.save()
                club_counter += 1
                print(f'{club_counter}/{self.max_club_number} club has been created', end='\r')
            except IntegrityError:
                print("This club name was already taken")

        print('Club seeding has been completed successfully')

    def generate_tournaments(self):
        tournament_counter = 0
        self.create_set_tournaments()
        print("Set tournaments created", end='\r')
        while tournament_counter < self.max_tournament_number:
            tournament = self.create_tournament(get_club())
            if tournament.deadline < make_aware(datetime.now()):
                if tournament.participants.count() > tournament.SIZE_OF_BRACKET:
                    generate_tournament_matches(tournament, random.randint(
                        int(tournament.participants.count() / tournament.NUMBER_OF_GROUPS),
                        int(tournament.participants.count() / tournament.NUMBER_OF_GROUPS + math.log2(
                            tournament.SIZE_OF_BRACKET))))
                else:
                    generate_tournament_matches(tournament,
                                                random.randint(2, int(math.log2(tournament.SIZE_OF_BRACKET))))

            try:
                tournament.full_clean()
                tournament.save()
                tournament_counter += 1
                print(f'{tournament_counter}/{self.max_tournament_number} tournament has been created', end='\r')
            except ValidationError:
                print("This tournament name was already taken")

        print('Tournament seeding has been completed successfully')

    def create_set_clubs(self):
        owner = get_user()
        kerbal = Club.objects.create(
            name='Kerbal Chess Club',
            location='Deep space',
            description='After our success with space programmes, we decided to start a chess club',
            owner=owner
        )
        kerbal.give_elo(owner)
        kerbal.make_member(User.objects.get(email='jeb@example.org'))
        kerbal.make_member(User.objects.get(email='val@example.org'))
        kerbal.make_member(User.objects.get(email='billie@example.org'))
        self.generate_club_users(kerbal)
        print('kerbal created')
        owner = get_user()
        new_york = Club.objects.create(
            name='New York Chess Club',
            location='New York',
            description='The Empire State Chess Club',
            owner=owner
        )
        new_york.give_elo(owner)
        new_york.make_member(User.objects.get(email='jeb@example.org'))
        new_york.make_officer(User.objects.get(email='jeb@example.org'))
        self.generate_club_users(new_york)
        print('new york created')
        owner = User.objects.get(email='val@example.org')
        amsterdam = Club.objects.create(
            name='Amsterdam Chess Club',
            location='Amsterdam',
            description='The Chess Club for the Dutch talent',
            owner=owner
        )
        amsterdam.give_elo(owner)
        self.generate_club_users(amsterdam)
        print('amsterdam created')
        owner = get_user()
        moscow = Club.objects.create(
            name='Moscow Chess Club',
            location='Moscow',
            description='The Russian School of chess',
            owner=owner
        )
        moscow.give_elo(owner)
        moscow.make_member(User.objects.get(email='billie@example.org'))
        self.generate_club_users(moscow)
        print('moscow created')

        kerbal.save()
        new_york.save()
        amsterdam.save()
        moscow.save()

    def create_set_tournaments(self):
        club = Club.objects.get(name='Kerbal Chess Club')
        for i in range(0, self.max_tournament_number_for_kerbal):
            tournament = self.create_tournament(club, past=True)
            generate_tournament_matches(tournament, finish=True)
            try:
                tournament.full_clean()
                tournament.save()
                print(f'{i + 1}/{self.max_tournament_number_for_kerbal} tournament has been created', end='\r')
            except ValidationError:
                print("This tournament name was already taken")

        create_future_tournament(club)
        create_current_tournament(club)

    def create_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        bio = self.faker.text(max_nb_chars=400)
        chess_exp = create_user_experience()
        personal_statement = self.faker.text(max_nb_chars=500)
        password = "pbkdf2_sha256$260000$VEDi9wsMYG6eNVeL8WSPqj$LHEiR2iUkusHCIeiQdWS+xQGC9/CjhhrjEOESMMp+c0="

        User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            bio=bio,
            chess_exp=chess_exp,
            personal_statement=personal_statement,
            password=password
        )

    def create_club(self):
        city = self.faker.city()
        name = self.faker.city() + ' Chess Club'
        location = city
        description = self.faker.text(400)
        owner = get_user()

        club = Club.objects.create(
            name=name,
            location=location,
            description=description,
            owner=owner
        )
        club.give_elo(owner)
        return club

    def create_tournament(self, club, past=False):
        name = f'{club.name} Tournament #{club.get_all_tournaments().count() + 1}'
        description = self.faker.text(max_nb_chars=500)
        officers = list(club.officers.all())
        random.shuffle(officers)
        organiser = officers[0]
        members = list(club.members.all())
        random.shuffle(members)
        participants = members[0: random.randint(4, len(members))]
        coorganisers = members[0: random.randint(0, 5)]
        if past:
            deadline = datetime.combine(self.faker.date_between(start_date='-1y', end_date='today'),
                                        datetime.now().time())
        else:
            deadline = datetime.combine(self.faker.date_between(start_date='-1y', end_date='+1y'),
                                        datetime.now().time())

        tournament = Tournament.objects.create(
            club=club,
            name=name,
            description=description,
            organiser=organiser,
            deadline=make_aware(deadline)
        )

        tournament.participants.set(participants)
        tournament.coorganisers.set(coorganisers)

        return tournament

    def generate_club_users(self, club):
        # make members
        members_list = get_number_of_applicants(club, self.number_of_members)
        for user in members_list:
            club.make_member(user)
        # make officers
        officer_list = get_number_of_applicants(club, self.number_of_officers)
        for user in officer_list:
            club.make_member(user)
            club.make_officer(user)
