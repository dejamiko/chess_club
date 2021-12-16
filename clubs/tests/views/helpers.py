from django.urls import reverse
from clubs.models import EloRating


def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url


def give_all_missing_elos(club):
    for user in club.get_all_users():
        try:
            EloRating.objects.get(user=user, club=club)
        except:
            club.give_elo(user)


class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
