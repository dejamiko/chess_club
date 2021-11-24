from django.shortcuts import redirect, render
from .models import User, Club
from .forms import SignUpForm, LogInForm, EditForm
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

# when log-in page is created, this will redirect there if current user not authenticated
@login_required
def user_list(request):
    # Temporary fake club with some members, officers and stuff
    club = Club.objects.get(name="Saint Louis Chess Club")

    if club.user_level(request.user) == 'Applicant':
        redirect('home_page')

    if request.GET.get("listed_user"):
        listed_user = User.objects.get(username=request.GET.get("listed_user"))

        # check request.user can actually do what they're trying to do
        listed_user.promote(club) if request.GET.get("promote") else None
        listed_user.demote(club) if request.GET.get("demote") else None
        if request.GET.get("switch_owner"):
            club.make_owner(listed_user)
            return redirect('home_page')

        return redirect("users")

    if request.user.user_level(club) == "Member":
        user_dict = club.get_members()
    else:
        user_dict = User.objects.all()

    user_dict_with_levels = []
    for user in user_dict:
        user_dict_with_levels.append((user, club.user_level(user)))

    # TODO filter the user_dict if a filter (by role / by chess exp) is in the GET
    # TODO sort (everything in that column alphabetically) the user_dict if a sort is in the GET

    return render(request, "user_list.html",
                  {"users": user_dict_with_levels, "user_level": request.user.user_level(club)})

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
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                redirect_url = request.POST.get('next') or 'home_page'
                return redirect(redirect_url) #for now home page is placeholder
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = LogInForm()
    next = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form, 'next': next})


def log_out(request):
    logout(request)
    return redirect('log_in')

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
