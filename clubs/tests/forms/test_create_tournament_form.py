"""Unit tests of the create tournament form."""
from django.test import TestCase
from clubs.forms import CreateTournamentForm
from clubs.models import User, Club, Tournament
from datetime import datetime
from django.utils.timezone import make_aware


class CreateTournamentFormTestCase(TestCase):
    """Unit tests of the create tournament form."""
    fixtures = ["clubs/tests/fixtures/default_user.json",
                "clubs/tests/fixtures/default_club.json",
                "clubs/tests/fixtures/other_users.json"]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.com")
        self.club = Club.objects.get(name="Saint Louis Chess Club")
        self.jane = User.objects.get(email="janedoe@example.com")
        self.bob = User.objects.get(email="bobdoe@example.com")
        self.form_input = {
            "club": self.club,
            "name": "Saint Louis Chess Tournament",
            "description": "An example chess tournament!",
            "organiser": self.user,
            "coorganisers": [self.jane, self.bob],
            "deadline_date": "10/12/2021",
            "deadline_time": "12:30"
        }

    def test_valid_create_tournament_form(self):
        form = CreateTournamentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = CreateTournamentForm()
        self.assertIn("name", form.fields)
        self.assertIn("description", form.fields)
        self.assertIn("coorganisers", form.fields)
        self.assertIn("deadline_date", form.fields)
        self.assertIn("deadline_time", form.fields)

    def test_form_rejects_blank_name(self):
        self.form_input["name"] = None
        form = CreateTournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_blank_coorganisers(self):
        self.form_input["coorganisers"] = []
        form = CreateTournamentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_deadline_date(self):
        self.form_input["deadline_date"] = None
        form = CreateTournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_deadline_time(self):
        self.form_input["deadline_time"] = None
        form = CreateTournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_coorganiser(self):
        self.form_input["coorganisers"] = ["invalid user"]
        form = CreateTournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = CreateTournamentForm(data=self.form_input)
        before_count = Tournament.objects.count()
        form.save(user=self.user, club=self.club.id)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count + 1)
        tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")

        self.assertEqual(tournament.club, self.club)
        self.assertEqual(tournament.name, "Saint Louis Chess Tournament")
        self.assertEqual(tournament.description, "An example chess tournament!")
        self.assertEqual(tournament.organiser, self.user)
        self.assertEqual(list(tournament.coorganisers.all()), [self.jane, self.bob])
        self.assertEqual(tournament.deadline, make_aware(datetime(2021, 10, 12, 12, 30)))