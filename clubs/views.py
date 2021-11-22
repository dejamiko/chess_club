from django.shortcuts import redirect, render
from .models import User, Member, make_owner, make_officer
from .forms import SignUpForm, LogInForm, EditForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required


# when log-in page is created, this will redirect there if current user not authenticated
@login_required
def user_list(request):
    # TODO if applicant, redirect straight to home

    if request.GET.get("listed_user"):
        listed_user = User.objects.get(username=request.GET.get("listed_user"))

        # check request.user can actually do what they're trying to do
        listed_user.promote() if request.GET.get("promote") else None
        listed_user.demote() if request.GET.get("demote") else None
        if request.GET.get("switch_owner"):
            make_owner(listed_user)
            make_officer(request.user)
            # FIXME redirect to homepage when it exists
            return redirect('home_page')

        return redirect("users")

    if request.user.user_level() == "Member":
        user_dict = Member.objects.all()
    else:
        user_dict = User.objects.all()

    # TODO filter the user_dict if a filter (by role / by chess exp) is in the GET
    # TODO sort (everything in that column alphabetically) the user_dict if a sort is in the GET

    return render(request, "user_list.html", {"users": user_dict})


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
            #User is logged out by default after password change
            #hence need for importing 'update_session_auth_hash'
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
            #print("-=-=-=-=-=-=-=-=FORM IS VALID STAGE
            #messages.add_message(request, messages.SUCCESS, "Profile updated!")
            #^^^^^^^^^^^^^^^^^^^^ appears on home page

            form.save()
            return redirect('profile')
    else:
        form = EditForm(instance=current_user)
    return render(request, 'edit_profile.html', {'form': form})


def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home_page') #for now home page is placeholder
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form})


def log_out(request):
    logout(request)
    return redirect('log_in')


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
