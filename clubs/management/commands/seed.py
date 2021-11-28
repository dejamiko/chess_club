from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User, Club
import random

class Command(BaseCommand):
    """The database seeder."""

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')


    def handle(self, *args, **options):
        user_arr = []
        user_counter = 0
        # while user_counter < 20:
        #     try:
        #         self.createUser()
        #         #x = self.createUser()
        #         #user_arr[user_counter] = x
        #     except:
        #         continue
        #     user_counter += 1
        #     print(user_counter)
        #createClub(user_arr)
        for x in range(100):
            y = self.createUser()
            user_arr.append(y)
            print(x)
        self.createClub(user_arr)
        print('User seeding has successfully been completed...')

    def createUser(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self.createEmail(first_name, last_name)
        bio = self.faker.text(max_nb_chars=400)
        chess_exp = self.createUserXP()
        personal_statement = self.faker.text(max_nb_chars=500)

        User.objects.create_user(
            first_name = first_name,
            last_name = last_name,
            email = self.faker.name() + self.faker.email(),
            bio = bio,
            chess_exp = chess_exp,
            personal_statement = personal_statement
        )
        return x


    def createUserXP(self):
        xp_levels = ['New to chess', 'Beginner', 'Intermediate', 'Advanced', 'Expert']
        xp_chooser = random.randint(0,4)
        return xp_levels[xp_chooser]


    def createEmail(self, first_name, last_name):
        email = f'{first_name.lower()}.{last_name.lower()}@fakerseed.org'
        return email
