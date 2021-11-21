from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User
import random

class Command(BaseCommand):
    """The database seeder."""

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')


    def handle(self, *args, **options):
        user_counter = 0
        while user_counter < 100:
            try:
                self.createUser()
            except:
                continue
            user_counter += 1


        print('User seeding has successfully been completed...')

    def createUser(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        username = self.createUsername(first_name, last_name)
        email = self.createEmail(first_name, last_name)
        bio = self.faker.text(max_nb_chars=400)
        chess_exp = self.createUserXP()
        personal_statement = self.faker.text(max_nb_chars=500)

        User.objects.create_user(
            username,
            first_name = first_name,
            last_name = last_name,
            email = email,
            bio = bio,
            chess_exp = chess_exp,
            personal_statement = personal_statement
        )


    def createUserXP(self):
        xp_levels = ['New to chess', 'Beginner', 'Intermediate', 'Advanced', 'Expert']
        xp_chooser = random.randint(0,4)
        return xp_levels[xp_chooser]


    def createEmail(self, first_name, last_name):
        email = f'{first_name.lower()}.{last_name.lower()}@fakerseed.org'
        return email

    def createUsername(self, first_name, last_name):
        username = f'{first_name}{last_name}'
        return username
