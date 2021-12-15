from django.contrib import admin

from .models import User, Tournament, Club, Match, Pairing, EloRating


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


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'winner', 'loser'
    ]


@admin.register(Pairing)
class PairingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tournament'
    ]


@admin.register(EloRating)
class EloRatingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'club', 'elo_rating'
    ]
