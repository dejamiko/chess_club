from django.core.management.base import BaseCommand
from clubs.models import User, Club


class Command(BaseCommand):
    """The database unseeder."""

    def handle(self, *args, **options):
        # email_substring = "@fakerseed.org"
        Club.objects.all().delete()
        print('All clubs have been unseeded')
        User.objects.filter(is_staff=False,
                            # email__contains=email_substring,
                            is_superuser=False).delete()
        print('All users have been unseeded')
