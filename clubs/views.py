from django.shortcuts import redirect, render
from .models import Tournament, User, Club, ClubApplicationModel, Pairing, pairing_to_match_elimination_phase
from .forms import SignUpForm, LogInForm, EditForm, CreateClubForm, CreateTournamentForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from django.utils.timezone import make_aware
from random import choice
from pathlib import Path

global club
club = None


def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect('home_page')
        else:
            return view_function(request)

    return modified_view_function


@login_required
def manage_applications(request):
    user = request.user
    if request.method == 'POST':
        username = request.POST.get('uname')  # the user to promote
        club_name = request.POST.get('clubname')  # the club they wish to become a member of
        temp_club = Club.objects.get(name=club_name)
        temp_user = User.objects.get(email=username)

        try:
            temp_app = ClubApplicationModel.objects.get(associated_club = temp_club,
            associated_user = temp_user
            )
        except ClubApplicationModel.DoesNotExist:
            temp_app = None

        if 'accepted' in request.POST:
            if temp_app is not None and temp_user not in temp_club.get_all_users():
                if temp_app.is_rejected == False:
                    temp_club.add_new_member(temp_user)
                    temp_club.save()
                    temp_app.delete()
                    return redirect('manage_applications')

        if 'rejected' in request.POST:
            if temp_app is not None and temp_user not in temp_club.get_all_users():
                if temp_app.is_rejected == False:
                    temp_app.is_rejected = True
                    temp_app.save()
                    return redirect('manage_applications')

        if 'revert' in request.POST:
            if temp_app is not None and temp_user not in temp_club.get_all_users():
                if temp_app.is_rejected == True:
                    temp_app.delete()
                    return redirect('manage_applications')

    applications = []
    try:
        temp = ClubApplicationModel.objects.filter(is_rejected = False)
    except ClubApplicationModel.DoesNotExist:
        temp = None
    for app in temp:
        if user in app.associated_club.get_officers() or user == app.associated_club.get_owner():
            applications.append(app)

    rejected_applications = []
    try:
        temp_rejected = ClubApplicationModel.objects.filter(is_rejected = True)
    except ClubApplicationModel.DoesNotExist:
        temp_rejected = None
    for rej_app in temp_rejected:
        if user in rej_app.associated_club.get_officers() or user == rej_app.associated_club.get_owner():
            rejected_applications.append(rej_app)

    user_clubs = user_clubs_finder(request)

    return render(request, 'manage_applications.html',
                  {'applications': applications, "user_clubs": user_clubs, "selected_club": club, 'rejected_applications': rejected_applications})


@login_required
def user_list_main(request, club_id):
    user_clubs = user_clubs_finder(request)
    try:
        club_verify = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        response = render(request, "no_access_screen.html", {"user_clubs": user_clubs})
        return response
    if user_clubs and club_verify in user_clubs:
        global club
        club = Club.objects.get(id=club_id)
        response = user_list(request, club)
        return response
    else:
        response = render(request, "no_access_screen.html", {"user_clubs": user_clubs})
        return response


@login_required
def user_list_no_club(request):
    user_clubs = user_clubs_finder(request)
    response = render(request, "no_club_screen.html", {"user_clubs": user_clubs})
    return response


def user_list_select_club(request):
    user_clubs = user_clubs_finder(request)
    response = render(request, "select_club_screen.html", {"user_clubs": user_clubs})
    return response

def get_occupied_users(curr_club):
        try:
            tournaments = Tournament.objects.filter(club= curr_club)
        except Tournament.DoesNotExist:
            tournaments = None

        occupied_users = []
        for t in tournaments:
            if (t.deadline < make_aware(datetime.now())) and (t.participants.count() > 0 ):
                occupied_users.append(t.organiser)
                if t.coorganisers.exists():
                    for c in t.coorganisers.all():
                        occupied_users.append(c)
                if t.participants.exists():
                    for p in t.participants.all():
                        occupied_users.append(p)
        return occupied_users

@login_required
def user_list(request, user_club):
    if request.user not in user_club.get_all_users():
        redirect('home_page')

    curr_user = request.user

    try:
        curr_tournaments = Tournament.objects.filter(club= user_club)
    except Tournament.DoesNotExist:
        curr_tournaments = None

    if request.method == 'POST':
        listed_user = User.objects.get(email=request.POST.get("listed_user"))
        if 'demote' in request.POST and listed_user.user_level(user_club) == 'Officer' and user_club.get_owner() == curr_user:
            listed_user.demote(user_club)
        if 'promote' in request.POST and listed_user.user_level(user_club) == 'Member' and \
        (curr_user.user_level(user_club) == 'Officer' or user_club.get_owner() ==curr_user) :
            listed_user.promote(user_club)
        if 'switch_owner' in request.POST and user_club.get_owner() == curr_user and listed_user.user_level(user_club) == 'Officer':
            user_club.make_owner(listed_user)
        if 'kick' in request.POST and listed_user.user_level(user_club) == 'Member' and \
        (curr_user.user_level(user_club) == 'Officer' or user_club.get_owner() ==curr_user):
            if listed_user not in get_occupied_users(user_club):
                if curr_tournaments is not None:
                    for t in curr_tournaments:
                        if (make_aware(datetime.now()) < t.deadline)or (make_aware(datetime.now()) > t.deadline and t.participants.count() == 0):
                            if listed_user == t.organiser:
                                # delete the tournament if kicking the owner
                                t.delete()
                            elif listed_user in t.coorganisers.all():
                                t.coorganisers.remove(listed_user)
                            elif listed_user in t.participants.all():
                                t.participants.remove(listed_user)

                user_club.members.remove(listed_user)

        return redirect("users", user_club.id)

    if request.user.user_level(user_club) == "Member":
        user_dict = user_club.get_members()
    else:
        user_dict = user_club.get_all_users()

    user_dict_with_levels = []
    for user in user_dict:
        user_dict_with_levels.append((user, user_club.user_level(user)))

    user_clubs = user_clubs_finder(request)

    try:
        tournaments = Tournament.objects.all()
    except Tournament.DoesNotExist:
        tournaments = None

    return render(request, "user_list.html",
                  {"users": user_dict_with_levels, "user_level": request.user.user_level(user_club),
                   "user_clubs": user_clubs, "selected_club": user_club, 'occupied_users': get_occupied_users(user_club),
                   'curr_tournaments': curr_tournaments, 'tournaments': tournaments})


@login_required
# Finds all clubs the logged in user belongs to and returns this information in a list
def user_clubs_finder(request):
    user_clubs = []

    clubs = Club.objects.all()
    for temp_club in clubs:
        if request.user in temp_club.get_all_users():
            user_clubs.append(temp_club)

    return user_clubs



@login_required
def club_list(request):
    curr_user = request.user
    if request.method == 'POST':
        club_name = request.POST.get('name')
        temp_club = Club.objects.get(name=club_name)

        try:
            temp_app = ClubApplicationModel.objects.get(associated_club = temp_club,
            associated_user = curr_user
            )
        except ClubApplicationModel.DoesNotExist:
            temp_app = None

        if temp_app is None and curr_user not in temp_club.get_all_users():
            club_application = ClubApplicationModel(
                associated_club=Club.objects.get(name=club_name),
                associated_user=curr_user)
            club_application.save()

    try:
        applications = ClubApplicationModel.objects.filter(is_rejected = False)
    except ClubApplicationModel.DoesNotExist:
        applications = None

    try:
        rejected_applications = ClubApplicationModel.objects.filter(is_rejected = True)
    except ClubApplicationModel.DoesNotExist:
        rejected_applications = None


    user_clubs = user_clubs_finder(request)
    return render(request, "club_list.html",
                  {"clubs": Club.objects.all(), 'applications': applications, 'curr_user': curr_user,
                   "user_clubs": user_clubs, "selected_club": club, "rejected_applications": rejected_applications})


@login_required
def home_page(request):
    user_clubs = user_clubs_finder(request)
    return render(request, 'home_page.html', {"date": date.today().strftime("%d/%m/%Y"),
                                              "pun": choice(open(Path(__file__).with_name("puns.txt")).readlines()),
                                              "today": make_aware(datetime.now()),
                                              # i was going to make puns.txt a static file, but apparently django
                                              # won't 'serve' them when debug mode will be turned off
                                              "incomplete_user_tournaments": _get_current_user_tournaments(user_clubs),
                                              "user_clubs": user_clubs, "selected_club": club})


def _get_current_user_tournaments(user_clubs):
    temp_list = []
    for club in user_clubs:
        for tournament in club.get_all_tournaments():
            if not tournament.winner:
                temp_list.append(tournament)
    return temp_list


@login_required
def profile(request, user_id):
    user_clubs = user_clubs_finder(request)
    try:
        requested_user = User.objects.get(id=user_id)
        all_user_clubs = requested_user.member_of.all().union(requested_user.officer_of.all()).union(requested_user.owner_of.all())
    except:
        if club:
            return redirect("users", club.id)
        else:
            return redirect("select_club")
    else:
        return render(request, "profile.html", {"requested_user": requested_user, "all_user_clubs": all_user_clubs, "user_clubs": user_clubs, "selected_club": club})


@login_prohibited
def welcome_screen(request):
    return render(request, 'welcome_screen.html')


@login_required
def change_password(request):
    current_user = request.user
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=current_user)
        if form.is_valid():
            form.save()
            # User is logged out by default after password change
            # hence need for importing 'update_session_auth_hash'
            update_session_auth_hash(request, form.user)
            return redirect('home_page')
    else:
        form = PasswordChangeForm(user=current_user)

    user_clubs = user_clubs_finder(request)

    return render(request, 'change_password.html', {'form': form, "user_clubs": user_clubs, "selected_club": club})


@login_required
def edit_profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = EditForm(request.POST, instance=current_user)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('profile', current_user.id)
    else:
        form = EditForm(instance=current_user)

    user_clubs = user_clubs_finder(request)

    return render(request, 'edit_profile.html', {'form': form, "user_clubs": user_clubs, "selected_club": club})


@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                redirect_url = request.POST.get('next') or 'home_page'

                return redirect(redirect_url)  # for now home page is placeholder
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")

    form = LogInForm()
    next_url = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form, 'next': next_url})


@login_required
def log_out(request):
    logout(request)
    global club
    club = None
    return redirect('welcome_screen')


@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home_page')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


@login_required
def create_club(request):
    if request.method == 'POST':
        form = CreateClubForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return redirect('clubs')
    else:
        form = CreateClubForm()
    user_clubs = user_clubs_finder(request)
    return render(request, 'create_club.html', {'form': form, "user_clubs": user_clubs, "selected_club": club})
    # redirect to home page with new club as drop down choice when user story done


@login_required
def create_tournament(request):
    user_clubs = user_clubs_finder(request)
    if user_clubs and club in user_clubs:
        if request.user.user_level(club) == "Officer" or request.user.user_level(club) == "Owner":
            if request.method == "POST":
                form = CreateTournamentForm(post=request.POST, club=club, current_user=request.user)
                if form.is_valid():
                    new_tournament = form.save(request.user, club.id)
                    return redirect("view_tournament", tournament_id=new_tournament.id)
            else:
                form = CreateTournamentForm(club=club, current_user=request.user)
            return render(request, "create_tournament.html", {"form": form, "user_clubs": user_clubs, "selected_club": club, "club_id": club.id})
        else:
            return redirect("home_page")
    else:
        response = render(request, "no_access_screen.html", {"user_clubs": user_clubs})
        return response


@login_required
def view_tournament(request, tournament_id):

    temp_user = request.user
    user_clubs = user_clubs_finder(request)
    try:
        tournament = Tournament.objects.get(id=tournament_id)
        if request.GET.get("create_pairings"):
            tournament.create_initial_pairings()
            return redirect("view_tournament", tournament_id)
        if request.GET.get("results_entered"):
            pairing = Pairing.objects.get(id=request.GET.get("pairing"))
            if request.GET.get("player"):
                match = pairing_to_match_elimination_phase(pairing, User.objects.get(id=request.GET.get("player")))
            else:
                match = pairing_to_match_elimination_phase(pairing)
            match.save()
            if tournament.all_pairings_completed() and not tournament.is_final:
                tournament.next_pairings()
            elif tournament.all_pairings_completed():
                tournament.set_winner(match.winner)
                tournament.save()
            return redirect("view_tournament", tournament_id)
    except Exception as e:
        return redirect("home_page")

    if request.method == 'POST' and 'Join_tournament' in request.POST:
        if temp_user not in tournament.get_all_participants() and make_aware(datetime.now()) < tournament.deadline:
            tournament.make_participant(temp_user)

    if request.method == 'POST' and 'Leave_tournament' in request.POST:
        if temp_user in tournament.get_all_participants() and make_aware(datetime.now()) < tournament.deadline :
            tournament.remove_participant(temp_user)

    return render(request, "view_tournament.html",
                     {"tournament": tournament, "deadline_passed": tournament.deadline < make_aware(datetime.now()), "user_clubs": user_clubs, "selected_club": club})



@login_required
def club_page(request, club_id):
    club = Club.objects.get(id=club_id)
    curr_user = request.user
    already_exists = False
    if request.method == 'POST':
        club_name = request.POST['name']
        temp_club = Club.objects.get(name=club_name)
        try:
            temp_app = ClubApplicationModel.objects.get(
            associated_club = temp_club,
            associated_user = curr_user
            )
        except ClubApplicationModel.DoesNotExist:
            temp_app = None
        if temp_app is None:
            club_application = ClubApplicationModel(
                associated_club=Club.objects.get(name=club_name),
                associated_user=curr_user)
            club_application.save()


    try:
        applications = ClubApplicationModel.objects.all()
    except ClubApplicationModel.DoesNotExist:
        applications = None
        return redirect('clubs')

    user_clubs = user_clubs_finder(request)
    return render(request, 'club_page.html',
        {'club': club, 'curr_user': request.user, "user_clubs": user_clubs, "selected_club": club})
