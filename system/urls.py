"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from clubs import views

urlpatterns = [
    path("admin", admin.site.urls),
    path("<club_id>/users", views.user_list_main, name="users"),
    path("create_tournament", views.create_tournament, name="create_tournament"),
    path("tournament/<tournament_id>", views.view_tournament, name="view_tournament"),
    path("owned_clubs", views.owned_club_list, name="owned_clubs"),
    path("clubs", views.club_list, name="clubs"),
    path("no_club", views.user_list_no_club, name="no_club"),
    path("select_club", views.user_list_select_club, name="select_club"),
    path("home", views.home_page, name="home_page"),
    path("sign_up", views.sign_up, name="sign_up"),
    path("", views.welcome_screen, name="welcome_screen"),
    path("log_in", views.log_in, name="log_in"),
    path("log_out", views.log_out, name='log_out'),
    path("user/<user_id>", views.profile, name='profile'),
    path("edit_profile", views.edit_profile, name='edit_profile'),
    path("change_password", views.change_password, name="change_password"),
    path("create_club", views.create_club, name="create_club"),
    path('manage_applications', views.manage_applications, name='manage_applications'),
    path("club/<int:club_id>", views.club_page, name="club_page"),
]
