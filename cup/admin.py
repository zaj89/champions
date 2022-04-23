from django.contrib import admin
from .models import Player, Match, Cup, Round, Invite


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('player1', 'player2', 'result1', 'result2', 'round', 'cup',)


@admin.register(Cup)
class CupAdmin(admin.ModelAdmin):
    list_display = ('name', 'number_of_players')
    search_fields = ('name',)


admin.site.register(Round)
admin.site.register(Invite)
