from django.contrib import admin

from .models import User, Tournament, Club


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "chess_exp"]

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name'
    ]

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'club', 'name'
    ]
