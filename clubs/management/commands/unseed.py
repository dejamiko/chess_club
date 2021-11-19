from django.core.management.base import BaseCommand, CommandError
from clubs.models import User

class Command(BaseCommand):
        """The database unseeder."""

        def handle(self, *args, **options):
             User.objects.filter(is_superuser = False).delete()
             #^this was needed for debugging log in issues
