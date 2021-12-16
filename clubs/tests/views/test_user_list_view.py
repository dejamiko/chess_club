"""Unit tests of the user list view"""
from django.test import TestCase
from django.urls import reverse
from clubs.tests.views.helpers import reverse_with_next
from clubs.models import User, Club, Tournament, EloRating, ClubApplication
from datetime import datetime, timedelta
from django.utils.timezone import make_aware


class UserListTest(TestCase):
    """Unit tests of the user list view"""
    fixtures = ["clubs/tests/fixtures/default_user.json", 'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json', "clubs/tests/fixtures/other_clubs.json",
                "clubs/tests/fixtures/default_elo.json", "clubs/tests/fixtures/other_elo.json"
                , 'clubs/tests/fixtures/default_tournament.json']

    def setUp(self):
        EloRating.objects.filter(pk=2).delete()
        EloRating.objects.filter(pk=3).delete()
        self.user = User.objects.get(email='janedoe@example.com')
        self.john = User.objects.get(email='johndoe@example.com')
        self.michael = User.objects.get(email='michaeldoe@example.com')
        self.bob = User.objects.get(email='bobdoe@example.com')
        self.alice = User.objects.get(email='alicedoe@example.com')
        self.club = Club.objects.get(name='Saint Louis Chess Club')
        self.other_club = Club.objects.get(name='Saint Louis Chess Club 2')
        self.tournament = Tournament.objects.get(name="Saint Louis Chess Tournament")
        #self.other_tournament = Tournament.objects.get(name="Bedroom Tournament")
        self.url = reverse("users", kwargs={'club_id': self.club.id})

    def test_user_list_url(self):
        self.assertEqual(self.url, "/1/users")

    def test_logged_in_redirect(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_applicant_cannot_access_list(self):
        new_applicant = ClubApplication.objects.create(associated_club = self.club,
        associated_user = self.user)
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, "no_access_screen.html")

    def test_member_can_only_see_members(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)

        self._create_test_users(start_id=5, count=5)
        self._create_test_users(start_id=10, count=5, level="Member")
        self._create_test_users(start_id=15, count=5, level="Officer")
        self._create_test_users(start_id=20, count=1, level="Owner")

        response = self._access_user_list_page()
        self.assertEqual(len(response.context["users"]), self.club.get_number_of_members())

        for user_id in range(5, 10):
            self.assertNotContains(response, f"First {user_id} Last {user_id}")

        for user_id in range(10, 15):
            self.assertContains(response, f"First {user_id} Last {user_id}")

        for user_id in range(15, 21):
            self.assertNotContains(response, f"First {user_id} Last {user_id}")

    def test_member_sees_limited_variables(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)

        response = self._access_user_list_page()
        self.assertContains(response, "Name")
        self.assertContains(response, "Chess experience")
        self.assertNotContains(response, "Email")
        self.assertNotContains(response, "Role")
        self.assertNotContains(response, "Options")

    def test_officer_can_see_everyone(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)

        self._create_test_users(start_id=5, count=5)
        self._create_test_users(start_id=10, count=5, level="Member")
        self._create_test_users(start_id=15, count=5, level="Officer")
        self._create_test_users(start_id=20, count=1, level="Owner")

        response = self._access_user_list_page()
        self.assertEqual(len(response.context["users"]), self.club.get_all_users().count())

        for user_id in range(10, 21):
            self.assertContains(response, f"First {user_id} Last {user_id}")
            self.assertContains(response, f"{user_id}@test.com")

    def test_officer_sees_all_variables(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)

        response = self._access_user_list_page()
        self.assertContains(response, "Name")
        self.assertContains(response, "Chess experience")
        self.assertContains(response, "Email")
        self.assertContains(response, "Role")
        self.assertContains(response, "Options")

    def test_owner_can_see_everyone(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)

        self._create_test_users(start_id=5, count=5)
        self._create_test_users(start_id=10, count=5, level="Member")
        self._create_test_users(start_id=15, count=5, level="Officer")
        self._create_test_users(start_id=20, count=1, level="Owner")

        response = self._access_user_list_page()
        self.assertEqual(len(response.context["users"]), self.club.get_all_users().count())

        for user_id in range(10, 21):
            self.assertContains(response, f"First {user_id} Last {user_id}")
            self.assertContains(response, f"{user_id}@test.com")

    def test_owner_sees_all_variables(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)

        response = self._access_user_list_page()
        self.assertContains(response, "Name")
        self.assertContains(response, "Chess experience")
        self.assertContains(response, "Email")
        self.assertContains(response, "Role")
        self.assertContains(response, "Options")

    def test_officer_has_promote_button_for_member(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)

        self._create_test_users(start_id=0, count=1, level="Member")

        response = self._access_user_list_page()
        self.assertContains(response, "Promote")

    def test_officer_has_no_promote_button_for_officer(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)

        self._create_test_users(start_id=0, count=1, level="Officer")

        response = self._access_user_list_page()
        self.assertNotContains(response, "Promote")

    def test_officer_has_no_promote_button_for_owner(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)

        self._create_test_users(start_id=0, count=1, level="Owner")

        response = self._access_user_list_page()
        self.assertNotContains(response, "Promote")

    def test_owner_has_no_promote_button_for_officer(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)

        self._create_test_users(start_id=0, count=1, level="Officer")

        response = self._access_user_list_page()
        self.assertNotContains(response, "Promote")

    def test_owner_has_demote_button_for_officer(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)

        self._create_test_users(start_id=0, count=1, level="Officer")

        response = self._access_user_list_page()
        self.assertContains(response, "Demote")

    def test_owner_has_switch_ownership_button_for_officer(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)

        self._create_test_users(start_id=0, count=1, level="Officer")

        response = self._access_user_list_page()
        self.assertContains(response, "Switch ownership")

    def test_promote_button(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_member(self.bob)

        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, {"listed_user": self.bob.email, "promote": "Promote"}, follow=True)
        self.assertContains(response, "Bob Doe was promoted to officer!")
        self.assertEqual(self.club.user_level(self.bob), "Officer")

    def test_demote_button(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_member(self.bob)
        self.club.make_officer(self.bob)

        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, {"listed_user": self.bob.email, "demote": "Demote"}, follow=True)
        self.assertContains(response, "Bob Doe was demoted to member!")
        self.assertEqual(self.club.user_level(self.bob), "Member")

    def test_switch_ownership_button(self):
        self.club.make_member(self.user)
        self.club.make_officer(self.user)
        self.club.make_owner(self.user)
        self.club.make_member(self.bob)
        self.club.make_officer(self.bob)

        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, {"listed_user": self.bob.email, "switch_owner": "Switch ownership"}, follow=True)
        self.assertContains(response, "You switched ownership with Bob Doe!")
        self.assertEqual(Club.objects.get(name="Saint Louis Chess Club").user_level(self.bob), "Owner")

    def _access_user_list_page(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_list.html")
        return response

    def _create_test_users(self, start_id=0, count=5, level="Applicant"):
        for user_id in range(start_id, start_id + count):
            temp_user = User.objects.create_user(
                id=user_id,
                first_name=f"First {user_id}",
                last_name=f"Last {user_id}",
                email=f"{user_id}@test.com",
                chess_exp="Beginner",
            )
            if level == "Owner":
                EloRating.objects.filter(user=temp_user, club=self.club).delete()
                self.club.add_new_member(temp_user)
                self.club.make_officer(temp_user)
                self.club.make_owner(temp_user)
            if level == "Officer":
                EloRating.objects.filter(user=temp_user, club=self.club).delete()
                self.club.add_new_member(temp_user)
                self.club.make_officer(temp_user)
            if level == "Member":
                EloRating.objects.filter(user=temp_user, club=self.club).delete()
                self.club.add_new_member(temp_user)

    def test_promote_button(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.client.login(email=self.john.email, password='Password123')
        self.client.get(self.url)
        self.assertNotIn(self.user, self.club.get_officers())
        self.client.post(self.url, {'listed_user': self.user.email, 'promote': True})
        self.assertIn(self.user, self.club.get_officers())

    def test_demote_button(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)
        self.client.login(email=self.john.email, password='Password123')
        self.client.get(self.url)
        self.assertNotIn(self.user, self.club.get_members())
        self.client.post(self.url, {'listed_user': self.user.email, 'demote': True})
        self.assertIn(self.user, self.club.get_members())

    def test_switch_ownership_button(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)
        self.client.login(email=self.john.email, password='Password123')
        self.client.get(self.url)
        self.assertNotEquals(self.user, self.club.get_owner())
        self.client.post(self.url, {'listed_user': self.user.email, 'switch_owner': True})
        updated_club = Club.objects.get(name=self.club.name)
        self.assertEquals(self.user, updated_club.get_owner())
        self.assertIn(self.john, updated_club.get_officers())

    def test_member_cannot_kick(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        EloRating.objects.filter(user=self.michael, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.add_new_member(self.michael)
        before_elo_count = EloRating.objects.count()
        self.client.login(email=self.user.email, password='Password123')
        self.client.get(self.url)
        #print(self.client.get(self.url).content)
        before_count1 = self.club.get_all_users().count()
        # Try kick Michael, a member, as a member
        self.client.post(self.url, {'listed_user': self.michael.email, 'kick': True})
        after_count1 = self.club.get_all_users().count()
        self.assertEqual(before_count1, after_count1)
        self.club.make_officer(self.michael)
        self.client.get(self.url)
        before_count2 = self.club.get_all_users().count()
        # Try kick Michael, now an officer, as a member
        self.client.post(self.url, {'listed_user': self.michael.email, 'kick': True})
        after_count2 = self.club.get_all_users().count()
        self.assertEqual(before_count2, after_count2)

        self.club.make_owner(self.michael)
        self.client.get(self.url)
        before_count3 = self.club.get_all_users().count()
        # Try kick Michael, now the OWNER, as a member
        self.client.post(self.url, {'listed_user': self.michael.email, 'kick': True})
        after_count3 = self.club.get_all_users().count()
        self.assertEqual(before_count3, after_count3)
        after_elo_count = EloRating.objects.count()
        self.assertEqual(before_elo_count, after_elo_count)

    def test_officer_can_kick_member_not_in_tournament(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        EloRating.objects.filter(user=self.michael, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.make_officer(self.user)
        self.club.add_new_member(self.michael)
        before_elo_count = EloRating.objects.count()
        self.client.login(email=self.user.email, password='Password123')
        self.client.get(self.url)
        before_count = self.club.get_all_users().count()
        self.client.post(self.url, {'listed_user': self.michael.email, 'kick': True})
        after_count = self.club.get_all_users().count()
        self.assertEqual(before_count, after_count+1)
        after_elo_count = EloRating.objects.count()
        self.assertEqual(before_elo_count, after_elo_count+1)

    def test_owner_can_kick_member_not_in_tournament(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        before_elo_count = EloRating.objects.count()
        self.client.login(email=self.john.email, password='Password123')
        self.client.get(self.url)
        before_count = self.club.get_all_users().count()
        self.client.post(self.url, {'listed_user': self.user.email, 'kick': True})
        after_count = self.club.get_all_users().count()
        self.assertEqual(before_count, after_count+1)
        after_elo_count = EloRating.objects.count()
        self.assertEqual(before_elo_count, after_elo_count+1)


    def test_can_kick_member_in_tournament_in_other_club(self):
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        before_elo_count = EloRating.objects.count()
        temp_other_tournament = Tournament.objects.create(
        club = self.other_club, name="other tournament", description="other", organiser = self.user,
        deadline = make_aware(datetime.now()+timedelta(days = 1))
        )
        before_tournament_count = Tournament.objects.count()
        self.client.login(email=self.john.email, password='Password123')
        self.client.get(self.url)
        before_count = self.club.get_all_users().count()
        self.client.post(self.url, {'listed_user': self.user.email, 'kick': True})
        after_count = self.club.get_all_users().count()
        after_tournament_count = Tournament.objects.count()
        self.assertEqual(before_count, after_count+1)
        self.assertEqual(before_tournament_count, after_tournament_count)
        after_elo_count = EloRating.objects.count()
        self.assertEqual(before_elo_count, after_elo_count+1)

    def test_can_kick_member_in_tournament_in_same_club_who_is_participant_that_has_not_started(self):
        # can kick a member in a tournament in the current club that has not started
        EloRating.objects.filter(user=self.michael, club=self.club).delete()
        self.club.add_new_member(self.michael)
        before_elo_count = EloRating.objects.count()
        self.client.login(email=self.john.email, password='Password123')
        self.client.get(self.url)
        before_count = self.club.get_all_users().count()
        self.client.post(self.url, {'listed_user': self.michael.email, 'kick': True})
        after_count = self.club.get_all_users().count()
        self.assertEqual(before_count, after_count+1)
        after_elo_count = EloRating.objects.count()
        self.assertEqual(before_elo_count, after_elo_count+1)


    def test_can_kick_member_in_tournament_in_same_club_who_is_coorganiser_that_has_not_started(self):
        # can kick a member in a tournament in the current club that has not started
        EloRating.objects.filter(user=self.bob, club=self.club).delete()
        self.club.add_new_member(self.bob)
        before_elo_count = EloRating.objects.count()
        self.client.login(email=self.john.email, password='Password123')
        self.client.get(self.url)
        before_count = self.club.get_all_users().count()
        self.client.post(self.url, {'listed_user': self.bob.email, 'kick': True})
        after_count = self.club.get_all_users().count()
        self.assertEqual(before_count, after_count+1)
        after_elo_count = EloRating.objects.count()
        self.assertEqual(before_elo_count, after_elo_count+1)

    def test_can_kick_member_in_tournament_in_same_club_who_is_owner_that_has_not_started(self):
        # should DELETE the tournament
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        before_elo_count = EloRating.objects.count()
        temp_other_tournament = Tournament.objects.create(
        club = self.club, name="other tournament", description="other", organiser = self.user,
        deadline = make_aware(datetime.now()+timedelta(days = 1))
        )
        before_tournament_count = Tournament.objects.count()
        self.client.login(email=self.john.email, password='Password123')
        self.client.get(self.url)
        before_count = self.club.get_all_users().count()
        self.client.post(self.url, {'listed_user': self.user.email, 'kick': True})
        after_count = self.club.get_all_users().count()
        after_tournament_count = Tournament.objects.count()
        self.assertEqual(before_count, after_count+1)
        self.assertEqual(before_tournament_count, after_tournament_count+1)
        after_elo_count = EloRating.objects.count()
        self.assertEqual(before_elo_count, after_elo_count+1)

    def test_can_kick_member_in_active_tournament_who_is_owner_that_has_no_participants(self):
        # should delete the tournament, as it has no participants and the organiser has been kicked
        # from the club
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        self.club.add_new_member(self.user)
        before_elo_count = EloRating.objects.count()
        temp_other_tournament = Tournament.objects.create(
        club = self.club, name="other tournament", description="other", organiser = self.user,
        deadline = make_aware(datetime.now()-timedelta(days = 1))
        )
        before_tournament_count = Tournament.objects.count()
        self.client.login(email=self.john.email, password='Password123')
        self.client.get(self.url)
        before_count = self.club.get_all_users().count()
        self.client.post(self.url, {'listed_user': self.user.email, 'kick': True})
        after_count = self.club.get_all_users().count()
        after_tournament_count = Tournament.objects.count()
        self.assertEqual(before_count, after_count+1)
        self.assertEqual(before_tournament_count, after_tournament_count+1)
        after_elo_count = EloRating.objects.count()
        self.assertEqual(before_elo_count, after_elo_count+1)


    def test_cannot_kick_member_who_is_in_active_tournament(self):
        # should not be able to kick a user in a tournament with 1 or more participants
        EloRating.objects.filter(user=self.user, club=self.club).delete()
        EloRating.objects.filter(user=self.bob, club=self.club).delete()
        self.club.add_new_member(self.user)
        self.club.add_new_member(self.bob)
        before_elo_count = EloRating.objects.count()
        temp_other_tournament = Tournament.objects.create(
        club = self.club, name="other tournament", description="other", organiser = self.user,
        deadline = make_aware(datetime.now()-timedelta(days = 1))
        )
        temp_other_tournament.participants.add(self.bob)
        temp_other_tournament.participants.add(self.alice)
        temp_other_tournament.save()
        before_tournament_count = Tournament.objects.count()
        self.client.login(email=self.john.email, password='Password123')
        self.client.get(self.url)
        before_count = self.club.get_all_users().count()
        self.client.post(self.url, {'listed_user': self.bob.email, 'kick': True})
        self.client.post(self.url, {'listed_user': self.user.email, 'kick': True})
        after_count = self.club.get_all_users().count()
        after_tournament_count = Tournament.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertEqual(before_tournament_count, after_tournament_count)
        after_elo_count = EloRating.objects.count()
        self.assertEqual(before_elo_count, after_elo_count)
