from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from faker import Faker
from clubs.models import User, Club
import random


class Command(BaseCommand):
    """The database seeder."""

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_counter = 0
        self.create_set_users()
        print("Set users created")
        while user_counter < 50:
            try:
                self.create_user()
                user_counter += 1
                print(user_counter.__str__() + ' user has been created')
            except IntegrityError:
                print("This username or email was already taken")
        print('User seeding has been completed successfully')
        club_counter = 0
        self.create_set_clubs()
        print("Set clubs created")
        while club_counter < 3:
            club = self.create_club()
            try:
                club.full_clean()
                club.save()
                club_counter += 1
                print(club_counter.__str__() + ' club has been created')
            except ValidationError:
                print("This club name was already taken")

        self.generate_club_users()
        print('Club seeding has been completed successfully')

    def create_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self.create_email(first_name, last_name)
        bio = self.faker.text(max_nb_chars=400)
        chess_exp = self.create_user_experience()
        personal_statement = self.faker.text(max_nb_chars=500)
        password = 'Password123'

        User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            bio=bio,
            chess_exp=chess_exp,
            personal_statement=personal_statement,
            password=password
        )

    def create_set_users(self):
        User.objects.create_user(
            first_name='Jebediah',
            last_name='Kerman',
            email='jeb@example.org',
            bio='Hi, I am Jeb',
            chess_exp='Beginner',
            personal_statement='I like chess a lot!',
            password='Password123'
        )
        User.objects.create_user(
            first_name='Valentina',
            last_name='Kerman',
            email='val@example.org',
            bio='Hi, I am Val',
            chess_exp='Advanced',
            personal_statement='Chess is a game of infinite beauty',
            password='Password123'
        )
        User.objects.create_user(
            first_name='Billie',
            last_name='Kerman',
            email='billie@example.org',
            bio='Hi, I am Billie',
            chess_exp='Intermediate',
            personal_statement='64 squares and billions of possibilities!',
            password='Password123'
        )

    def create_club(self):
        city = self.faker.city()
        name = self.faker.city() + ' Chess Club'
        location = city
        description = self.faker.text(400)
        owner = self.get_user()

        club = Club.objects.create(
            name=name,
            location=location,
            description=description,
            owner=owner
        )

        return club

    def create_set_clubs(self):
        owner = self.get_user()
        kerbal = Club.objects.create(
            name='Kerbal Chess Club',
            location='Deep space',
            description='After our success with space programmes, we decided to start a chess club',
            owner=owner
        )
        kerbal.make_member(User.objects.get(email='jeb@example.org'))
        kerbal.make_member(User.objects.get(email='val@example.org'))
        kerbal.make_member(User.objects.get(email='billie@example.org'))
        print('kerbal created')
        owner = self.get_user()
        new_york = Club.objects.create(
            name='New York Chess Club',
            location='New York',
            description='The Empire State Chess Club',
            owner=owner
        )
        new_york.make_member(User.objects.get(email='jeb@example.org'))
        new_york.make_officer(User.objects.get(email='jeb@example.org'))
        print('new york created')
        owner = User.objects.get(email='val@example.org')
        amsterdam = Club.objects.create(
            name='Amsterdam Chess Club',
            location='Amsterdam',
            description='The Chess Club for the Dutch talent',
            owner=owner
        )
        print('amsterdam created')
        owner = self.get_user()
        moscow = Club.objects.create(
            name='Moscow Chess Club',
            location='Moscow',
            description='The Russian School of chess',
            owner=owner
        )
        moscow.make_member(User.objects.get(email='billie@example.org'))
        print('moscow created')

        kerbal.save()
        new_york.save()
        amsterdam.save()
        moscow.save()

    def generate_club_users(self):
        for club in Club.objects.all():
            while club.get_number_of_members() < 7:
                user = self.get_applicant(club)
                club.make_member(user)
            while club.get_number_of_officers() < 3:
                user = self.get_applicant(club)
                club.make_member(user)
                club.make_officer(user)

    def get_user(self):
        return list(User.objects.all())[random.randint(0, User.objects.count() - 1)]

    def get_applicant(self, club):
        possible = User.objects.all().difference(club.get_all_users())
        return possible[random.randint(0, len(possible) - 1)]

    def create_user_experience(self):
        xp_levels = ['New to chess', 'Beginner', 'Intermediate', 'Advanced', 'Expert']
        xp_chooser = random.randint(0, 4)
        return xp_levels[xp_chooser]

    def create_email(self, first_name, last_name):
        email = f'{first_name.lower()}.{last_name.lower()}@fakerseed.org'
        return email
