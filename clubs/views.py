from django.shortcuts import redirect, render
from .models import User, Club, ClubApplicationModel
from .forms import SignUpForm, LogInForm, EditForm, CreateClubForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required


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
        uname =  request.POST.get('uname') #the user to promote
        print("----------POST USERNAME" + uname)
        clubname = request.POST.get('clubname') #the club they wish to become a member of
        print("----------CLUB NAME" + clubname)
        temp_club = Club.objects.get(name=clubname)
        temp_user = User.objects.get(username=uname)
        temp_club.make_member(temp_user)
        temp_club.save()
        delform = ClubApplicationModel.objects.get(associated_club =temp_club, associated_user = temp_user)
        delform.delete() #bad practice?
        return redirect('manage_applications')
    temp = []
    applications = []
    try:
        temp = ClubApplicationModel.objects.all()
    except ClubApplicationModel.DoesNotExist:
        temp = None
    for app in temp:
        if user in app.associated_club.get_officers() or user == app.associated_club.get_owner():
            applications.append(app)
    return render(request, 'manage_applications.html', {'applications': applications})


@login_required
def user_list(request):
    # Temporary fake club with some members, officers and stuff
    club = Club.objects.get(location='london')

    if club.user_level(request.user) == 'Applicant':
        redirect('home_page')

    if request.GET.get("listed_user"):
        listed_user = User.objects.get(email=request.GET.get("listed_user"))

        listed_user.promote(club) if request.GET.get("promote") else None
        listed_user.demote(club) if request.GET.get("demote") else None
        club.make_owner(listed_user) if request.GET.get(
            "switch_owner") else None

        return redirect("users")

    if request.user.user_level(club) == "Member":
        user_dict = club.get_members()
    else:
        user_dict = User.objects.all()

    user_dict_with_levels = []
    for user in user_dict:
        user_dict_with_levels.append((user, club.user_level(user)))

    return render(request, "user_list.html",
                  {"users": user_dict_with_levels, "user_level": request.user.user_level(club)})


@login_required
def club_list(request):
    curr_user = request.user
    all_clubs = Club.objects.all()
    already_exists = False
    if request.method == 'POST':
        club_name =  request.POST['name']
        temp_club = Club.objects.get(name=club_name)
        club_applicants = temp_club.get_all_applicants()
        for applicant in club_applicants:
            if applicant == curr_user:
                already_exists = True
                print("APPLICANT ALREADY EXISTS")

        if already_exists == False:
            print("CLUB NAME TO APPLY TO -------------------- " + club_name)
            clubapplication = ClubApplicationModel(
            associated_club = Club.objects.get(name=club_name),
            associated_user = curr_user )
            clubapplication.save()
            temp_club = Club.objects.get(name=club_name)
            temp_club.make_applicant(curr_user)
            temp_club.save()

    try:
        applications = ClubApplicationModel.objects.all()
    except ClubApplicationModel.DoesNotExist:
        applications = None

    return render(request, "club_list.html", {"clubs": Club.objects.all(), 'applications': applications, 'curr_user': curr_user})


@login_required
def home_page(request):
    return render(request, 'home_page.html')


@login_required
def profile(request):
    return render(request, 'profile.html', {'curr_user': request.user})


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
    return render(request, 'change_password.html', {'form': form})


@login_required
def edit_profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = EditForm(request.POST, instance=current_user)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('profile')
    else:
        form = EditForm(instance=current_user)
    return render(request, 'edit_profile.html', {'form': form})

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
                # for now home page is placeholder
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR,
                             "The credentials provided were invalid!")
    form = LogInForm()
    next = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form, 'next': next})


def log_out(request):
    logout(request)
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
