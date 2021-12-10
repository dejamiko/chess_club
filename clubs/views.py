from django.shortcuts import redirect, render
from requests.models import to_native_string
from .models import Tournament, User, Club, ClubApplicationModel
from .forms import SignUpForm, LogInForm, EditForm, CreateClubForm, CreateTournamentForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from django.utils.timezone import make_aware
from requests import get

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
        temp_club.make_member(temp_user)
        temp_club.save()
        form_to_be_deleted = ClubApplicationModel.objects.get(associated_club=temp_club, associated_user=temp_user)
        form_to_be_deleted.delete()  # bad practice?
        return redirect('manage_applications')
    applications = []
    try:
        temp = ClubApplicationModel.objects.all()
    except ClubApplicationModel.DoesNotExist:
        temp = None
    for app in temp:
        if user in app.associated_club.get_officers() or user == app.associated_club.get_owner():
            applications.append(app)

    user_clubs = user_clubs_finder(request)

    return render(request, 'manage_applications.html',
                  {'applications': applications, "user_clubs": user_clubs, "selected_club": club})


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


@login_required
def user_list(request, user_club):
    if user_club.user_level(request.user) == 'Applicant':
        redirect('home_page')

    if request.GET.get("listed_user"):
        listed_user = User.objects.get(email=request.GET.get("listed_user"))

        listed_user.promote(user_club) if request.GET.get("promote") else None
        listed_user.demote(user_club) if request.GET.get("demote") else None
        user_club.make_owner(listed_user) if request.GET.get(
            "switch_owner") else None

        return redirect("users", user_club.id)

    if request.user.user_level(user_club) == "Member":
        user_dict = user_club.get_members()
    else:
        user_dict = user_club.get_all_users()

    user_dict_with_levels = []
    for user in user_dict:
        user_dict_with_levels.append((user, user_club.user_level(user)))

    user_clubs = user_clubs_finder(request)

    return render(request, "user_list.html",
                  {"users": user_dict_with_levels, "user_level": request.user.user_level(user_club),
                   "user_clubs": user_clubs, "selected_club": user_club})


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
    already_exists = False
    if request.method == 'POST':
        club_name = request.POST['name']
        temp_club = Club.objects.get(name=club_name)
        club_applicants = temp_club.get_all_applicants()
        for applicant in club_applicants:
            if applicant == curr_user:
                already_exists = True
        if not already_exists:
            club_application = ClubApplicationModel(
                associated_club=Club.objects.get(name=club_name),
                associated_user=curr_user)
            club_application.save()
            temp_club = Club.objects.get(name=club_name)
            temp_club.make_applicant(curr_user)
            temp_club.save()

    try:
        applications = ClubApplicationModel.objects.all()
    except ClubApplicationModel.DoesNotExist:
        applications = None

    user_clubs = user_clubs_finder(request)
    return render(request, "club_list.html",
                  {"clubs": Club.objects.all(), 'applications': applications, 'curr_user': curr_user,
                   "user_clubs": user_clubs, "selected_club": club})


@login_required
def home_page(request):
    user_clubs = user_clubs_finder(request)
    return render(request, 'home_page.html', {"date": date.today().strftime("%d/%m/%Y"),
                                              "user_tournaments": _get_current_user_tournaments(user_clubs),
                                              "lichess_data": _get_lichess_data(),
                                              "user_clubs": user_clubs, "selected_club": club})


def _get_current_user_tournaments(user_clubs):
    temp_list = []
    for club in user_clubs:
        for tournament in club.get_all_tournaments():
            if not tournament.winner or tournament.deadline < make_aware(datetime.now()):
                temp_list.append(tournament)
    return temp_list


def _get_lichess_data():
    temp_list = []
    for tournament in get("https://lichess.org/api/tournament").json()["started"]:
        temp_list.append({
            "id": tournament["id"],
            "name": tournament["fullName"],
            "players": tournament["nbPlayers"],
            "starts": make_aware(datetime.fromtimestamp(tournament["startsAt"]/1000)),
            "ends": make_aware(datetime.fromtimestamp(tournament["finishesAt"]/1000)),
            "speed": tournament["schedule"]["speed"][0].upper() + tournament["schedule"]["speed"][1:]
        })
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
            return redirect('home_page')
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
    user_clubs = user_clubs_finder(request)
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except:
        return redirect("home_page")
    else:
        return render(request, "view_tournament.html",
                      {"tournament": tournament, "deadline_passed": tournament.deadline < make_aware(datetime.now()), "user_clubs": user_clubs, "selected_club": club})
