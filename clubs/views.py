from django.shortcuts import redirect, render
from .models import User, make_owner, make_officer


# from django.contrib.auth.decorators import login_required
# @login_required
# when log-in page is created, this will redirect there if current user not authenticated
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

        return redirect("users")

    if request.user.user_level == "Member":
        user_dict = User.objects.filter(user_level='Member')
    else:
        user_dict = User.objects.all()

    # TODO filter the user_dict if a filter (by role / by chess exp) is in the GET
    # TODO sort (everything in that column alphabetically) the user_dict if a sort is in the GET

    return render(request, "user_list.html", {"users": user_dict})
