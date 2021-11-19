from django.shortcuts import redirect, render
from .models import User, Member, make_owner, make_officer
from .forms import SignUpForm, LogInForm, EditProfile
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
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


@login_required
def edit_profile(request):
    #the profile to be edited
    profile = EditProfile(instance=request.user)
    return render(request, 'edit_profile.html', {'profile': profile})



    return render(request, 'edit_profile.html', )


def welcome_screen(request):
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
    return render(request, 'welcome_screen.html', {'login_form': form})

def log_out(request):
    logout(request)
    return redirect('welcome')


def sign_up(request):
     if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home_page')
     else:
        form = SignUpForm()
     return render(request, 'sign_up.html', {'signup_form': form})
