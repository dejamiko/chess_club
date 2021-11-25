from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Club

class Command(BaseCommand):
        """The database unseeder."""

        def handle(self, *args, **options):
             email_substring = "@fakerseed.org"
             User.objects.filter(is_staff=False, email__contains=email_substring, is_superuser=False).delete()
             print('All users have been unseeded...')
             Club.objects.all().delete()
