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
        username = self.faker.name()
        email = self.faker.email()
        bio = self.faker.text(max_nb_chars=400)
        chess_exp = self.createUserXP()
        personal_statement = self.faker.text(max_nb_chars=500)

        x = User.objects.create_user(
            username = self.faker.name()+self.faker.name(),
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

    def createUsername(self, first_name, last_name):
        username = f'{first_name}{last_name}'
        return username

    def createClub(self, user_array):
        locations = ['paris', 'london',
        'helsinki', 'tokyo', 'beijing'
        ]
        counter = 0
        for i in range (0,5):
            print(i)
            temp1 = user_array[counter]
            temp2 = user_array[counter+1]
            temp3 = user_array[counter+2]
            identifier = self.faker.name()
            c = Club(
            owner = temp3,
            name=identifier,
            location = locations[i],
            description = self.faker.text()
            )
            c.save()
            counter = counter + 3
            print(counter)
            temp = Club.objects.get(location=locations[i])
            temp.members.add(temp1)
            temp.officers.add(temp2)
            # temp.owner.set(temp3)
            # c.save()
