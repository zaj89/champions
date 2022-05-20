import random
from random import shuffle
from champ.views import when_user_authenticated_add_variables_menu

# import pywhatkit
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from account.models import Profile, ProfileInCup

from .forms import (
    CupForm,
    MatchCupForm,
    MatchLeagueForm,
    PlayerForm,
    PlayerWithTeamForm,
)
from .models import Cup, Invite, Match, Round


def Match_in_cup_not_played(cup):
    matches_in_cup = Match.objects.filter(cup=cup)
    match_in_cup_not_played = False
    for match in list(matches_in_cup):
        if match.finished:
            pass
        else:
            match_in_cup_not_played = True
    return {"match_in_cup_not_played": match_in_cup_not_played}


def Match_not_confirmed(cup):
    match_not_confirmed = False
    matches = Match.objects.filter(cup=cup)
    for match in list(matches):
        if match.confirmed:
            pass
        else:
            match_not_confirmed = True
    return match_not_confirmed


def Match_in_groups_not_played(cup):
    matches_in_groups = Match.objects.filter(cup__groupanothercup=cup)
    match_in_groups_not_played = False
    for match in list(matches_in_groups):
        if match.finished:
            pass
        else:
            match_in_groups_not_played = True
    return match_in_groups_not_played


def Match_not_played(cup):
    matches = Match.objects.filter(cup=cup)
    match_not_played = False
    for match in list(matches):
        if match.finished:
            pass
        else:
            match_not_played = True
    return match_not_played


def ordering_players(cup, players):
    len_players = 0
    for player in players:
        len_players += 1
        cup.players_order = str(cup.players_order) + str(player.id) + ","
    if len_players % 2 == 0:
        pass
    else:
        cup.players_order = cup.players_order + "pausing,"
    cup.save()


def add_pausing_if_number_of_profile_players_is_odd(players, ordering):
    for player_id in ordering:
        if player_id != "pausing":
            players.append(ProfileInCup.objects.get(id=player_id))
        else:
            players.append("pausing")


@login_required
def cups_list_offline(request):
    """
    It takes a request and a list of cups and returns a rendered template of cups_list.html

    :return: A rendered version of cups_list.html with the cups variable passed to the template engine.
    The view displays a list of cups
    """
    cups = (
        Cup.objects.filter(
            author=request.user, declarations="Ręczna", groupanothercup=None
        )
        .exclude(archived=True)
        .order_by("-id")
    )
    context = {
        "cups": cups,
    }
    if request.user.is_authenticated:
        context.update(when_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "cups_list.html",
        context,
    )


@login_required
def my_cups_list_online(request, user_id: int):
    """
    It takes a request and a list of cups and returns a rendered template of cups_list.html

    :return: A rendered version of cups_list.html with the cups variable passed to the template engine.
    The view displays a list of cups
    """
    cups = (
        Cup.objects.filter(author_id=user_id, archived=False)
        .exclude(declarations="Ręczna")
        .order_by("-id")
    )

    context = {
        "cups": cups,
    }
    if request.user.is_authenticated:
        context.update(when_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "cups_list.html",
        context,
    )


@login_required
def delete(request, cup_id: int):
    """
    Delete a cup from the database

    :type cup_id: int
    :param cup_id: The id of the cup to delete
    :return: Redirection to the cup list.
    """
    cup_to_del = Cup.objects.get(id=cup_id)
    cup_to_del.delete()
    messages.success(request, "Rozgrywki zostały skasowane.")
    return HttpResponseRedirect("/")


@login_required
def cup_new(request):
    """
    Creates a new cup.

    :return: Redirection to the list of players.
    """
    if request.method == "POST":
        cup_form = CupForm(data=request.POST)
        if cup_form.is_valid():
            new_cup = cup_form.save(commit=False)
            new_cup.author = request.user
            new_cup.save()
            messages.success(request, "Rozgrywki zostały utworzone.")
            # profile = Profile.objects.get(user=request.user)
            # pywhatkit.sendwhatmsg(str(profile.phone), f'Utworzyłeś rozgrywki {new_cup.name}.', 14, 23)
            return HttpResponseRedirect(
                "/cup/dashboard/{}/edit_players".format(new_cup.id)
            )
    else:
        cup_form = CupForm()
    context = {
        "cup_form": cup_form,
    }
    if request.user.is_authenticated:
        context.update(when_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "cup_new.html",
        context,
    )


@login_required
def dashboard(request, cup_id: int):
    """
    This function is used to display the dashboard of a cup

    :param cup_id: The id of the cup that we want to see the dashboard of
    :return: A rendered template of dashboard.html
    """

    cup = Cup.objects.get(id=cup_id)
    matches_in_cup = Match.objects.filter(cup=cup)
    context = {}
    if cup.type == "GrupyPuchar1mecz" or cup.type == "GrupyPuchar2mecze":
        groups = Cup.objects.filter(groupanothercup=cup)
        rounds_in_groups = Round.objects.filter(cup__groupanothercup=cup).order_by(
            "match", "id"
        )
        matches_in_groups = Match.objects.filter(cup__groupanothercup=cup)
        matches_in_cup = Match.objects.filter(cup=cup)
        match_in_groups_not_played = Match_in_groups_not_played(cup)
        context.update(Match_in_cup_not_played(cup))
    else:
        groups = None
        rounds_in_groups = None
        matches_in_groups = None
        match_in_groups_not_played = None
    matches = Match.objects.filter(cup=cup)
    match_not_played = Match_not_played(cup)
    match_not_confirmed = Match_not_confirmed(cup)
    if (
        cup.type == "Puchar"
        or cup.type == "GrupyPuchar1mecz"
        or cup.type == "GrupyPuchar2mecze"
    ):
        rounds = Round.objects.filter(cup=cup).order_by("match", "-id")
    else:
        rounds = Round.objects.filter(cup=cup).order_by("match", "id")
    players = ProfileInCup.objects.filter(cup=cup).order_by(
        "-points", "-goals_bilans", "-goals_scored"
    )
    profiles = Profile.objects.filter(user__in=cup.players.all())
    context.update(
        {
            "cup": cup,
            "matches": matches,
            "groups": groups,
            "matches_in_groups": matches_in_groups,
            "matches_in_cup": matches_in_cup,
            "rounds_in_groups": rounds_in_groups,
            "match_not_played": match_not_played,
            "match_in_groups_not_played": match_in_groups_not_played,
            "match_not_confirmed": match_not_confirmed,
            "rounds": rounds,
            "players": players,
            "profiles": profiles,
        }
    )
    if request.user.is_authenticated:
        context.update(when_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "dashboard.html",
        context,
    )


@login_required
def stats(request, cup_id: int):
    """
    The view displays the cup statistics.

    :param cup_id: The id of the cup you want to see the stats of
    :return: A rendered template of the stats.html page.
    """
    cup = Cup.objects.get(id=cup_id)
    players_goals = ProfileInCup.objects.filter(cup=cup).order_by("-goals_bilans")
    matches = Match.objects.filter(cup=cup)
    match_not_played = Match_not_played(cup)
    rounds = Round.objects.filter(cup=cup)[::-1]
    context = {
        "cup": cup,
        "matches": matches,
        "match_not_played": match_not_played,
        "rounds": rounds,
        "players_goals": players_goals,
    }
    if request.user.is_authenticated:
        context.update(when_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "stats.html",
        context,
    )


@login_required
def edit_players(request, cup_id: int):
    """
    It renders the edit_players.html template,
    which is used to add new players to the cup.

    :param cup_id: ID of the cup we want to edit the player list
    :return: A rendered template of the edit_players.html page.
    """
    cup = Cup.objects.get(id=cup_id)
    players = ProfileInCup.objects.filter(cup=cup)
    profiles = Profile.objects.filter(user__in=cup.players.all())
    profiles_in_cup = ProfileInCup.objects.filter(cup=cup)
    if cup.registration == "Otwarta":
        if request.method == "POST":
            if not cup.choosing_teams:
                player_form = PlayerForm(data=request.POST)
            else:
                player_form = PlayerWithTeamForm(data=request.POST)
            if player_form.is_valid():
                new_player = player_form.save(commit=False)
                new_player.cup = cup
                new_player.save()
                cup.number_of_players += 1
                cup.save()
                messages.success(request, f'Gracz "{new_player.name}" został dodany.')
                return HttpResponseRedirect(
                    "/cup/dashboard/{}/edit_players".format(cup.id)
                )
        else:
            if not cup.choosing_teams:
                player_form = PlayerForm()
            else:
                player_form = PlayerWithTeamForm()
    else:
        if not cup.choosing_teams:
            player_form = PlayerForm()
        else:
            player_form = PlayerWithTeamForm()
    players_search = None
    if cup.declarations == "Na zaproszenie":
        search_post = request.GET.get("search")
        if search_post:
            players_search = User.objects.filter(
                Q(username__icontains=search_post)
                & Q(first_name__icontains=search_post)
                & Q(id__exact=search_post)
            )
            messages.success(request, f"Wyświetlono znalezionych użytkowników")
    context = {
        "cup": cup,
        "players": players,
        "players_search": players_search,
        "profiles": profiles,
        "profiles_in_cup": profiles_in_cup,
        "player_form": player_form,
    }
    if request.user.is_authenticated:
        context.update(when_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "edit_players.html",
        context,
    )


@login_required
def edit_players_online(request, cup_id: int):
    global players_search
    cup = Cup.objects.get(id=cup_id)
    players = ProfileInCup.objects.filter(cup=cup)
    profiles = Profile.objects.all()
    profiles_in_cup = ProfileInCup.objects.filter(cup=cup)
    invitations_sent = Invite.objects.filter(cup=cup, status="Wysłano")
    players_search = None
    if cup.declarations == "Na zaproszenie":
        search_post = request.GET.get("search")
        if search_post:
            try:
                int(search_post)
                players_search = User.objects.filter(id=int(search_post))
            except ValueError:
                players_search = User.objects.filter(
                    Q(username__icontains=search_post)
                    & Q(first_name__icontains=search_post)
                )
            player_invited = False
            for invite in invitations_sent:
                for player in list(players_search):
                    if player == invite.to_player:
                        player_invited = True
            context = {
                "cup": cup,
                "players": players,
                "players_search": players_search,
                "invitations_sent": invitations_sent,
                "player_invited": player_invited,
                "profiles": profiles,
                "profiles_in_cup": profiles_in_cup,
            }
            if request.user.is_authenticated:
                context.update(when_user_authenticated_add_variables_menu(request))
            return render(
                request,
                "edit_players.html",
                context,
            )
        else:
            context = {
                "cup": cup,
                "players": players,
                "players_search": players_search,
                "invitations_sent": invitations_sent,
                "profiles": profiles,
                "profiles_in_cup": profiles_in_cup,
            }
            if request.user.is_authenticated:
                context.update(when_user_authenticated_add_variables_menu(request))
            return render(
                request,
                "edit_players.html",
                context,
            )
    elif cup.declarations == "Otwarta":
        return HttpResponseRedirect("/cup/dashboard/{}/edit_players".format(cup.id))


@login_required
def del_players(request, cup_id: int, player_to_del: int):
    """
    It deletes a player from the database and updates the number of players in the cup

    :param cup_id: The ID of the cup you want to edit
    :param player_to_del: The id of the player to delete
    :return: A redirect to the edit_players view.
    """
    cup = Cup.objects.get(id=cup_id)
    if cup.registration == "Otwarta":
        player_to_delete = ProfileInCup.objects.get(id=player_to_del)
        player_to_delete.delete()
        cup.number_of_players -= 1
        cup.save()
        messages.success(request, f'Gracz "{player_to_delete.name}" został skasowany.')
        return HttpResponseRedirect("/cup/dashboard/{}/edit_players".format(cup.id))
    else:
        messages.error(
            request,
            f"Rejestracja rozgrywek {cup.name} jest zamknięta. Nie można edytować graczy.",
        )
        return HttpResponseRedirect("/cup/dashboard/{}/edit_players".format(cup.id))


@login_required
def close_registration(request, cup_id: int):
    """
    It closes the registration for the cup.

    :param cup_id: The ID of the cup that you want to close the registration for
    :return: A rendered template of the dashboard.html page.
    """
    cup = Cup.objects.get(id=cup_id)
    players = list(ProfileInCup.objects.filter(cup=cup))
    if cup.registration == "Otwarta":
        if cup.declarations == "Otwarta":
            if cup.type == "Puchar":
                if len(players) < 4:
                    messages.success(
                        request,
                        "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 4 graczy.",
                    )
                    return HttpResponseRedirect(
                        "/cup/dashboard/{}/edit_players".format(cup.id)
                    )
                elif len(players) == 4:
                    len_rounds = 2
                elif 4 < len(players) < 8:
                    len_rounds = 2
                    cup.elimination_matches = len(players) - 4
                elif len(players) == 8:
                    len_rounds = 3
                elif 8 < len(players) < 16:
                    len_rounds = 3
                    cup.elimination_matches = len(players) - 8
                elif len(players) == 16:
                    len_rounds = 4
                elif 16 < len(players) < 32:
                    len_rounds = 5
                    cup.elimination_matches = len(players) - 16
                elif len(players) == 32:
                    len_rounds = 5
                elif 32 < len(players) < 64:
                    len_rounds = 6
                    cup.elimination_matches = len(players) - 32
                elif len(players) == 64:
                    len_rounds = 6
                elif 64 < len(players) < 120:
                    len_rounds = 7
                    cup.elimination_matches = len(players) - 64
                else:
                    len_rounds = 7
                for player in players:
                    profile = Profile.objects.get(user=player.user)
                    player.team = profile.team
                    player.save()
                cup.len_rounds = len_rounds
                cup.registration = "Zamknięta"
                cup.save()
                messages.success(request, "Rejestracja została zamknięta.")
                return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")

            elif cup.type == "GrupyPuchar1mecz" or cup.type == "GrupyPuchar2mecze":
                if len(players) < 8:
                    messages.success(
                        request,
                        "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 8 graczy.",
                    )
                    return HttpResponseRedirect(
                        "/cup/dashboard/{}/edit_players".format(cup.id)
                    )
                else:
                    shuffle(players)
                    cup.registration = "Zamknięta"
                    ordering_players(cup, players)

                messages.success(request, "Rejestracja została zamknięta.")
                return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
            elif cup.type == "1 mecz":
                if len(players) < 4:
                    messages.success(
                        request,
                        "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 4 graczy.",
                    )
                    return HttpResponseRedirect(
                        "/cup/dashboard/{}/edit_players".format(cup.id)
                    )
                else:
                    shuffle(players)
                    cup.registration = "Zamknięta"
                    ordering_players(cup, players)
                    for player in players:
                        profile = Profile.objects.get(user=player.user)
                        player.team = profile.team
                        player.save()
                    messages.success(request, "Rejestracja została zamknięta.")
                    return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
            elif cup.type == "2 mecze":
                if len(players) < 4:
                    messages.success(
                        request,
                        "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 4 graczy.",
                    )
                    return HttpResponseRedirect(
                        "/cup/dashboard/{}/edit_players".format(cup.id)
                    )
                else:
                    shuffle(players)
                    cup.registration = "Zamknięta"
                    ordering_players(cup, players)
                    if cup.declarations != "Ręczna":
                        for player in players:
                            profile = Profile.objects.get(user=player.user)
                            player.team = profile.team
                            player.save()
                    messages.success(request, "Rejestracja została zamknięta.")
                    return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
        elif cup.declarations == "Ręczna":
            if cup.type == "Puchar":
                if len(players) < 4:
                    messages.success(
                        request,
                        "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 4 graczy.",
                    )
                    return HttpResponseRedirect(
                        "/cup/dashboard/{}/edit_players".format(cup.id)
                    )
                elif len(players) == 4:
                    len_rounds = 2
                elif 4 < len(players) < 8:
                    len_rounds = 2
                    cup.elimination_matches = len(players) - 4
                elif len(players) == 8:
                    len_rounds = 3
                elif 8 < len(players) < 16:
                    len_rounds = 3
                    cup.elimination_matches = len(players) - 8
                elif len(players) == 16:
                    len_rounds = 4
                elif 16 < len(players) < 32:
                    len_rounds = 5
                    cup.elimination_matches = len(players) - 16
                elif len(players) == 32:
                    len_rounds = 5
                elif 32 < len(players) < 64:
                    len_rounds = 6
                    cup.elimination_matches = len(players) - 32
                elif len(players) == 64:
                    len_rounds = 6
                elif 64 < len(players) < 120:
                    len_rounds = 7
                    cup.elimination_matches = len(players) - 64
                else:
                    len_rounds = 7
                cup.len_rounds = len_rounds
                cup.registration = "Zamknięta"
                cup.save()
                messages.success(request, "Rejestracja została zamknięta.")
                return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
            elif cup.type == "GrupyPuchar1mecz" or cup.type == "GrupyPuchar2mecze":
                if len(players) < 8:
                    messages.success(
                        request,
                        "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 8 graczy.",
                    )
                    return HttpResponseRedirect(
                        "/cup/dashboard/{}/edit_players".format(cup.id)
                    )
                else:
                    shuffle(players)
                    cup.registration = "Zamknięta"
                    ordering_players(cup, players)
                    messages.success(request, "Rejestracja została zamknięta.")
                    return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
            elif cup.type == "1 mecz":
                if len(players) < 4:
                    messages.success(
                        request,
                        "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 4 graczy.",
                    )
                    return HttpResponseRedirect(
                        "/cup/dashboard/{}/edit_players".format(cup.id)
                    )
                else:
                    shuffle(players)
                    cup.registration = "Zamknięta"
                    ordering_players(cup, players)
                    if cup.declarations != "Ręczna":
                        for player in players:
                            profile = Profile.objects.get(user=player.user)
                            player.team = profile.team
                            player.save()
                    messages.success(request, "Rejestracja została zamknięta.")
                    return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")

            elif cup.type == "2 mecze":
                if len(players) < 4:
                    messages.success(
                        request,
                        "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 4 graczy.",
                    )
                    return HttpResponseRedirect(
                        "/cup/dashboard/{}/edit_players".format(cup.id)
                    )
                else:
                    shuffle(players)
                    cup.registration = "Zamknięta"
                    ordering_players(cup, players)
                    if cup.declarations != "Ręczna":
                        for player in players:
                            profile = Profile.objects.get(user=player.user)
                            player.team = profile.team
                            player.save()
                    messages.success(request, "Rejestracja została zamknięta.")
                    return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
        elif cup.declarations == "Na zaproszenie":
            if cup.type == "Puchar":
                if len(players) < 4:
                    messages.success(
                        request,
                        "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 4 graczy.",
                    )
                    return HttpResponseRedirect(
                        "/cup/dashboard/{}/edit_players".format(cup.id)
                    )
                elif len(players) == 4:
                    len_rounds = 2
                elif 4 < len(players) < 8:
                    len_rounds = 2
                    cup.elimination_matches = len(players) - 4
                elif len(players) == 8:
                    len_rounds = 3
                elif 8 < len(players) < 16:
                    len_rounds = 3
                    cup.elimination_matches = len(players) - 8
                elif len(players) == 16:
                    len_rounds = 4
                elif 16 < len(players) < 32:
                    len_rounds = 5
                    cup.elimination_matches = len(players) - 16
                elif len(players) == 32:
                    len_rounds = 5
                elif 32 < len(players) < 64:
                    len_rounds = 6
                    cup.elimination_matches = len(players) - 32
                elif len(players) == 64:
                    len_rounds = 6
                elif 64 < len(players) < 120:
                    len_rounds = 7
                    cup.elimination_matches = len(players) - 64
                else:
                    len_rounds = 7
                if cup.declarations != "Ręczna":
                    for player in players:
                        profile = Profile.objects.get(user=player.user)
                        player.team = profile.team
                        player.save()
                cup.len_rounds = len_rounds
                cup.registration = "Zamknięta"
                cup.save()
                messages.success(request, "Rejestracja została zamknięta.")
                return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")

            elif cup.type == "GrupyPuchar1mecz" or cup.type == "GrupyPuchar2mecze":
                if len(players) < 8:
                    messages.success(
                        request,
                        "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 8 graczy.",
                    )
                    return HttpResponseRedirect(
                        "/cup/dashboard/{}/edit_players".format(cup.id)
                    )
                else:
                    shuffle(players)
                    cup.registration = "Zamknięta"
                    ordering_players(cup, players)
                    messages.success(request, "Rejestracja została zamknięta.")
                    return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
            elif cup.type == "1 mecz":
                if len(players) < 4:
                    messages.success(
                        request,
                        "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 4 graczy.",
                    )
                    return HttpResponseRedirect(
                        "/cup/dashboard/{}/edit_players".format(cup.id)
                    )
                else:
                    shuffle(players)
                    cup.registration = "Zamknięta"
                    ordering_players(cup, players)
                    for player in players:
                        profile = Profile.objects.get(user=player.user)
                        player.team = profile.team
                        player.save()
                    messages.success(request, "Rejestracja została zamknięta.")
                    return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")

            elif cup.type == "2 mecze":
                if len(players) < 4:
                    messages.success(
                        request,
                        "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 4 graczy.",
                    )
                    return HttpResponseRedirect(
                        "/cup/dashboard/{}/edit_players".format(cup.id)
                    )
                else:
                    shuffle(players)
                    cup.registration = "Zamknięta"
                    ordering_players(cup, players)
                    if cup.declarations != "Ręczna":
                        for player in players:
                            profile = Profile.objects.get(user=player.user)
                            player.team = profile.team
                            player.save()
                    messages.success(request, "Rejestracja została zamknięta.")
                    return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
    else:
        messages.error(request, "Rejestracja już jest zamknięta.")
        return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")


@login_required
def generate_round(request, cup_id: int):
    """
    Generate new round for cup

    :param cup_id: int The ID of the cup you want to generate a round for
    :return: A rendered template of the dashboard.html page.
    """
    cup = Cup.objects.get(id=cup_id)
    if not cup.finished:
        if cup.type == "Puchar":
            match_not_played = Match_not_played(cup)
            if match_not_played:
                messages.error(
                    request,
                    "Nie rozegrano wszystkich meczy. Wprowadź wszystkie wyniki.",
                )
                return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
            else:
                new_round = Round.objects.create(cup=cup)
                if cup.actual_round is not None:
                    finished_round = Round.objects.get(id=cup.actual_round.id)
                    for player_prom in list(finished_round.promotion.all()):
                        new_round.players.add(player_prom)
                if not cup.elimination_generated and cup.elimination_matches > 0:
                    players = list(ProfileInCup.objects.filter(cup=cup))
                    new_round.name = "Eliminacje"
                    for new_match in range(cup.elimination_matches):
                        player1 = random.choice(players)
                        players.remove(player1)
                        player2 = random.choice(players)
                        players.remove(player2)
                        Match.objects.create(
                            player1=player1, player2=player2, cup=cup, round=new_round
                        )
                        new_round.players.add(player1)
                        new_round.players.add(player2)
                    for player in players:
                        new_round.promotion.add(player)
                    new_round.save()
                    cup.elimination_generated = True
                    cup.save()
                else:
                    if cup.actual_round:
                        players = list(cup.actual_round.promotion.all())
                    else:
                        players = list(ProfileInCup.objects.filter(cup=cup))
                    if len(players) == 2:
                        new_round.name = "Finał"
                    elif len(players) == 4:
                        new_round.name = "Półfinał"
                    elif len(players) == 8:
                        new_round.name = "Ćwierćfinał"
                    elif len(players) == 16:
                        new_round.name = "1/8 Finału"
                    elif len(players) == 32:
                        new_round.name = "1/16 Finału"
                    elif len(players) == 64:
                        new_round.name = "1/32 Finału"
                    elif len(players) == 128:
                        new_round.name = "1/64 Finału"
                    for new_match in range(len(players) // 2):
                        player1 = random.choice(players)
                        players.remove(player1)
                        player2 = random.choice(players)
                        players.remove(player2)
                        match = Match.objects.create(
                            player1=player1, player2=player2, cup=cup, round=new_round
                        )
                        new_round.players.add(match.player1)
                        new_round.players.add(match.player2)
                    new_round.save()

                cup.actual_round = new_round
                cup.save()
                messages.success(request, f"Wygenerowano {cup.actual_round}.")
                return HttpResponseRedirect("/cup/dashboard/{}/".format(cup.id))
        elif cup.type == "1 mecz":
            global ordering
            ordering = list(cup.players_order[:-1].split(","))
            if len(ordering) % 2 == 0:
                all_rounds = len(ordering)
            else:
                all_rounds = len(ordering) + 1
            players = []
            add_pausing_if_number_of_profile_players_is_odd(players, ordering)
            for round_nr in range(all_rounds)[1:]:
                actual_round = []
                if round_nr == 1:
                    new_round = Round.objects.create(
                        cup=cup, name=f"Kolejka {round_nr}"
                    )
                    for match in range(len(players) // 2):
                        if players[0] == "pausing":
                            pausing = players.pop(-1)
                            new_round.pausing = pausing
                            new_round.save()
                            players.remove(players[0])
                        elif players[-1] == "pausing":
                            pausing = players.pop(0)
                            new_round.pausing = pausing
                            new_round.save()
                            players.remove(players[-1])
                        else:
                            actual_round.append([players.pop(0), players.pop(-1)])
                    for match in actual_round:
                        if round_nr % 2 == 0:
                            Match.objects.create(
                                player1=match[0],
                                player2=match[1],
                                cup=cup,
                                round=new_round,
                            )
                        else:
                            Match.objects.create(
                                player1=match[1],
                                player2=match[0],
                                cup=cup,
                                round=new_round,
                            )
                else:
                    players = []
                    new_ordering = [ordering[0], ordering[-1]]
                    for player in ordering[1:-1]:
                        new_ordering.append(player)
                    ordering = new_ordering
                    add_pausing_if_number_of_profile_players_is_odd(players, ordering)
                    new_round = Round.objects.create(
                        cup=cup, name=f"Kolejka {round_nr}"
                    )
                    for match in range(len(players) // 2):
                        if players[0] == "pausing":
                            pausing = players.pop(-1)
                            players.remove(players[0])
                            new_round.pausing = pausing
                            new_round.save()
                        elif players[-1] == "pausing":
                            pausing = players.pop(0)
                            players.remove(players[-1])
                            new_round.pausing = pausing
                            new_round.save()
                        else:
                            actual_round.append([players.pop(0), players.pop(-1)])
                    for match in actual_round:
                        if round_nr % 2 == 0:
                            Match.objects.create(
                                player1=match[0],
                                player2=match[1],
                                cup=cup,
                                round=new_round,
                            )
                        else:
                            Match.objects.create(
                                player1=match[1],
                                player2=match[0],
                                cup=cup,
                                round=new_round,
                            )
            cup.len_rounds = all_rounds
            cup.league_generated = True
            cup.save()
            messages.success(request, "Rozgrywki wygenerowane.")
            return HttpResponseRedirect("/cup/dashboard/{}/".format(cup.id))
        elif cup.type == "2 mecze":
            ordering = list(cup.players_order[:-1].split(","))
            if len(ordering) % 2 == 0:
                all_rounds = len(ordering)
            else:
                all_rounds = len(ordering) + 1
            players = []
            add_pausing_if_number_of_profile_players_is_odd(players, ordering)
            for round_nr in range(all_rounds)[1:]:
                actual_round = []
                if round_nr == 1:
                    new_round = Round.objects.create(
                        cup=cup, name=f"Kolejka {round_nr}", match=1
                    )
                    new_round2 = Round.objects.create(
                        cup=cup, name=f"Kolejka {round_nr + all_rounds - 1}", match=2
                    )
                    for match in range(len(players) // 2):
                        if players[0] == "pausing":
                            pausing = players.pop(-1)
                            new_round.pausing = pausing
                            new_round.save()
                            new_round2.pausing = pausing
                            new_round2.save()
                            players.remove(players[0])
                        elif players[-1] == "pausing":
                            pausing = players.pop(0)
                            new_round.pausing = pausing
                            new_round.save()
                            new_round2.pausing = pausing
                            new_round2.save()
                            players.remove(players[-1])
                        else:
                            actual_round.append([players.pop(0), players.pop(-1)])
                    for match in actual_round:
                        if round_nr % 2 == 0:
                            Match.objects.create(
                                player1=match[0],
                                player2=match[1],
                                cup=cup,
                                round=new_round,
                            )
                            Match.objects.create(
                                player1=match[1],
                                player2=match[0],
                                cup=cup,
                                round=new_round2,
                            )
                        else:
                            Match.objects.create(
                                player1=match[1],
                                player2=match[0],
                                cup=cup,
                                round=new_round,
                            )
                            Match.objects.create(
                                player1=match[0],
                                player2=match[1],
                                cup=cup,
                                round=new_round2,
                            )

                else:
                    players = []
                    new_ordering = [ordering[0], ordering[-1]]
                    for player in ordering[1:-1]:
                        new_ordering.append(player)
                    ordering = new_ordering
                    add_pausing_if_number_of_profile_players_is_odd(players, ordering)
                    new_round = Round.objects.create(
                        cup=cup, name=f"Kolejka {round_nr}", match=1
                    )
                    new_round2 = Round.objects.create(
                        cup=cup, name=f"Kolejka {round_nr + all_rounds - 1}", match=2
                    )
                    for match in range(len(players) // 2):
                        if players[0] == "pausing":
                            pausing = players.pop(-1)
                            players.remove(players[0])
                            new_round.pausing = pausing
                            new_round.save()
                            new_round2.pausing = pausing
                            new_round2.save()
                        elif players[-1] == "pausing":
                            pausing = players.pop(0)
                            players.remove(players[-1])
                            new_round.pausing = pausing
                            new_round.save()
                            new_round2.pausing = pausing
                            new_round2.save()
                        else:
                            actual_round.append([players.pop(0), players.pop(-1)])
                    for match in actual_round:
                        if round_nr % 2 == 0:
                            Match.objects.create(
                                player1=match[0],
                                player2=match[1],
                                cup=cup,
                                round=new_round,
                            )
                            Match.objects.create(
                                player1=match[1],
                                player2=match[0],
                                cup=cup,
                                round=new_round2,
                            )
                        else:
                            Match.objects.create(
                                player1=match[1],
                                player2=match[0],
                                cup=cup,
                                round=new_round,
                            )
                            Match.objects.create(
                                player1=match[0],
                                player2=match[1],
                                cup=cup,
                                round=new_round2,
                            )
            cup.len_rounds = all_rounds
            cup.league_generated = True
            cup.save()
            messages.success(request, "Rozgrywki wygenerowane.")
            return HttpResponseRedirect("/cup/dashboard/{}/".format(cup.id))
        elif cup.type == "GrupyPuchar1mecz":
            if not cup.league_generated:
                players = list(ProfileInCup.objects.filter(cup=cup))
                if len(players) > 128:
                    len_group = 32
                elif len(players) > 64:
                    len_group = 16
                elif len(players) > 32:
                    len_group = 8
                elif len(players) > 16:
                    len_group = 4
                elif len(players) > 8:
                    len_group = 2
                else:
                    len_group = 2
                ordering = list(cup.players_order[:-1].split(","))
                if "pausing" in ordering:
                    ordering.remove("pausing")
                ordering_in_groups = [[] for _ in range(len_group)]
                len_while = 1
                while ordering:
                    if len_while <= len_group:
                        ordering_in_groups[len_while - 1].append(ordering.pop(0))
                        len_while += 1
                    else:
                        len_while = 1
                for index, group in enumerate(ordering_in_groups):
                    if len(group) % 2 != 0:
                        ordering_in_groups[index].append("pausing")
                for nr_group in range(len_group + 1)[1:]:
                    if len(ordering_in_groups[nr_group - 1]) % 2 == 0:
                        all_rounds = len(ordering_in_groups[nr_group - 1])
                    else:
                        all_rounds = len(ordering_in_groups[nr_group - 1]) + 1
                    players = []
                    ordering_to_group = ""
                    for pl_id in ordering_in_groups[nr_group - 1]:
                        ordering_to_group += pl_id + ","
                    ordering_to_group = list(ordering_to_group[:-1].split(","))
                    new_group = Cup.objects.create(
                        type="1 mecz",
                        name=str(str(nr_group) + "_grupa_" + cup.name),
                        author=request.user,
                        choosing_teams=cup.choosing_teams,
                        online=cup.online,
                        declarations=cup.declarations,
                        groupanothercup=cup,
                        players_order=ordering_to_group,
                        league_generated=True,
                        registration=cup.registration,
                    )
                    for player_id in ordering_in_groups[nr_group - 1]:
                        if player_id:
                            if player_id != "pausing":
                                player_to_add = ProfileInCup.objects.get(id=player_id)
                                player_to_add.group = new_group
                                player_to_add.save()
                                players.append(player_to_add)
                            else:
                                players.append("pausing")
                        else:
                            continue
                    for round_nr in range(all_rounds)[1:]:
                        actual_round = []
                        if round_nr == 1:
                            new_round = Round.objects.create(
                                cup=new_group, name=f"Kolejka {round_nr}"
                            )
                            for match in range(len(players) // 2):
                                if players[0] == "pausing":
                                    pausing = players.pop(-1)
                                    new_round.pausing = pausing
                                    new_round.save()
                                    players.remove(players[0])
                                elif players[-1] == "pausing":
                                    pausing = players.pop(0)
                                    new_round.pausing = pausing
                                    new_round.save()
                                    players.remove(players[-1])
                                else:
                                    pl1 = players.pop(0)
                                    pl2 = players.pop(-1)
                                    actual_round.append([pl1, pl2])
                            for match in actual_round:
                                if round_nr % 2 == 0:
                                    Match.objects.create(
                                        player1=match[0],
                                        player2=match[1],
                                        cup=new_group,
                                        round=new_round,
                                    )
                                else:
                                    Match.objects.create(
                                        player1=match[1],
                                        player2=match[0],
                                        cup=new_group,
                                        round=new_round,
                                    )
                            new_round.league_generated = True
                            new_round.save()
                        else:
                            players = []
                            new_ordering = [ordering_to_group[0], ordering_to_group[-1]]
                            for player in ordering_to_group[1:-1]:
                                new_ordering.append(player)
                            ordering_to_group = new_ordering
                            for player_id in ordering_to_group:
                                if player_id != "pausing":
                                    player_to_add = ProfileInCup.objects.get(
                                        id=player_id
                                    )
                                    player_to_add.group = new_group
                                    player_to_add.save()
                                    players.append(player_to_add)
                                else:
                                    players.append("pausing")
                            new_round = Round.objects.create(
                                cup=new_group, name=f"Kolejka {round_nr}"
                            )
                            for match in range(len(players) // 2):
                                if players[0] == "pausing":
                                    pausing = players.pop(-1)
                                    players.remove(players[0])
                                    new_round.pausing = pausing
                                    new_round.save()
                                elif players[-1] == "pausing":
                                    pausing = players.pop(0)
                                    players.remove(players[-1])
                                    new_round.pausing = pausing
                                    new_round.save()
                                else:
                                    actual_round.append(
                                        [players.pop(0), players.pop(-1)]
                                    )
                            for match in actual_round:
                                if round_nr % 2 == 0:
                                    Match.objects.create(
                                        player1=match[0],
                                        player2=match[1],
                                        cup=new_group,
                                        round=new_round,
                                    )
                                else:
                                    Match.objects.create(
                                        player1=match[1],
                                        player2=match[0],
                                        cup=new_group,
                                        round=new_round,
                                    )
                            new_round.league_generated = True
                            new_round.save()
                cup.len_rounds = all_rounds
                cup.league_generated = True
                cup.save()
                messages.success(request, "Faza grupowa wygenerowana.")
                return HttpResponseRedirect("/cup/dashboard/{}/".format(cup.id))
            else:
                if not cup.cupgenerated:
                    groups = Cup.objects.filter(groupanothercup=cup)
                    cup = Cup.objects.get(id=cup_id)
                    for group in groups:
                        players = ProfileInCup.objects.filter(group=group).order_by(
                            "-points"
                        )[:2]
                        for player in players:
                            group.promotion.add(player)
                            group.save()
                            cup.promotion.add(player)
                            cup.save()
                    cup.cupgenerated = True
                players = list(cup.promotion.all())
                shuffle(players)
                cup.save()
                new_round = Round.objects.create(cup=cup)
                match_not_played = Match_not_played(cup)
                if match_not_played:
                    messages.error(
                        request,
                        "Nie rozegrano wszystkich meczy. Wprowadź wszystkie wyniki.",
                    )
                    return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
                else:
                    if cup.actual_round is not None:
                        finished_round = Round.objects.get(id=cup.actual_round.id)
                        for player_prom in list(finished_round.promotion.all()):
                            new_round.players.add(player_prom)
                    if cup.actual_round:
                        players = list(cup.actual_round.promotion.all())
                    if len(players) == 2:
                        new_round.name = "Finał"
                    elif len(players) == 4:
                        new_round.name = "Półfinał"
                    elif len(players) == 8:
                        new_round.name = "Ćwierćfinał"
                    elif len(players) == 16:
                        new_round.name = "1/8 Finału"
                    elif len(players) == 32:
                        new_round.name = "1/16 Finału"
                    elif len(players) == 64:
                        new_round.name = "1/32 Finału"
                    elif len(players) == 128:
                        new_round.name = "1/64 Finału"
                    for new_match in range(len(players) // 2):
                        player1 = random.choice(players)
                        players.remove(player1)
                        player2 = random.choice(players)
                        players.remove(player2)
                        match = Match.objects.create(
                            player1=player1, player2=player2, cup=cup, round=new_round
                        )
                        new_round.players.add(match.player1)
                        new_round.players.add(match.player2)
                    new_round.save()

                    cup.actual_round = new_round
                    cup.save()
                    messages.success(request, f"Wygenerowano {cup.actual_round}.")
                    return HttpResponseRedirect("/cup/dashboard/{}/".format(cup.id))
        elif cup.type == "GrupyPuchar2mecze":
            if not cup.league_generated:
                players = list(ProfileInCup.objects.filter(cup=cup))
                if len(players) > 128:
                    len_group = 32
                elif len(players) > 64:
                    len_group = 16
                elif len(players) > 32:
                    len_group = 8
                elif len(players) > 16:
                    len_group = 4
                elif len(players) > 8:
                    len_group = 2
                else:
                    len_group = 2
                ordering = list(cup.players_order[:-1].split(","))
                if "pausing" in ordering:
                    ordering.remove("pausing")
                ordering_in_groups = [[] for _ in range(len_group)]
                len_while = 1
                all_rounds = 0
                while ordering:
                    if len_while <= len_group:
                        ordering_in_groups[len_while - 1].append(ordering.pop(0))
                        len_while += 1
                    else:
                        len_while = 1
                for index, group in enumerate(ordering_in_groups):
                    if len(group) % 2 != 0:
                        ordering_in_groups[index].append("pausing")
                for nr_group in range(len_group + 1)[1:]:
                    if len(ordering_in_groups[nr_group - 1]) % 2 == 0:
                        all_rounds = len(ordering_in_groups[nr_group - 1])
                    else:
                        all_rounds = len(ordering_in_groups[nr_group - 1]) + 1
                    players = []
                    ordering_to_group = ""
                    for pl_id in ordering_in_groups[nr_group - 1]:
                        ordering_to_group += pl_id + ","
                    ordering_to_group = list(ordering_to_group[:-1].split(","))
                    new_group = Cup.objects.create(
                        type="2 mecze",
                        name=str(str(nr_group) + "_grupa_" + cup.name),
                        author=request.user,
                        choosing_teams=cup.choosing_teams,
                        online=cup.online,
                        declarations=cup.declarations,
                        groupanothercup=cup,
                        players_order=ordering_to_group,
                        league_generated=True,
                        registration=cup.registration,
                    )
                    for player_id in ordering_in_groups[nr_group - 1]:
                        if player_id:
                            if player_id != "pausing":
                                player_to_add = ProfileInCup.objects.get(id=player_id)
                                player_to_add.group = new_group
                                player_to_add.save()
                                players.append(player_to_add)
                            else:
                                players.append("pausing")
                        else:
                            continue
                    for round_nr in range(all_rounds)[1:]:
                        actual_round = []
                        if round_nr == 1:
                            new_round = Round.objects.create(
                                cup=new_group, name=f"Kolejka {round_nr}"
                            )
                            new_round2 = Round.objects.create(
                                cup=new_group,
                                name=f"Kolejka {round_nr + all_rounds - 1}",
                                match=2,
                            )
                            for match in range(len(players) // 2):
                                if players[0] == "pausing":
                                    pausing = players.pop(-1)
                                    new_round.pausing = pausing
                                    new_round.save()
                                    players.remove(players[0])
                                    players.remove(pausing)
                                elif players[-1] == "pausing":
                                    pausing = players.pop(0)
                                    new_round.pausing = pausing
                                    new_round.save()
                                    players.remove(players[-1])
                                else:
                                    pl1 = players.pop(0)
                                    pl2 = players.pop(-1)
                                    actual_round.append([pl1, pl2])
                            for match in actual_round:
                                if round_nr % 2 == 0:
                                    Match.objects.create(
                                        player1=match[0],
                                        player2=match[1],
                                        cup=new_group,
                                        round=new_round,
                                    )
                                    Match.objects.create(
                                        player1=match[1],
                                        player2=match[0],
                                        cup=new_group,
                                        round=new_round2,
                                    )
                                else:
                                    Match.objects.create(
                                        player1=match[1],
                                        player2=match[0],
                                        cup=new_group,
                                        round=new_round,
                                    )
                                    Match.objects.create(
                                        player1=match[0],
                                        player2=match[1],
                                        cup=new_group,
                                        round=new_round2,
                                    )
                            new_round.league_generated = True
                            new_round.save()
                        else:
                            players = []
                            new_ordering = [ordering_to_group[0], ordering_to_group[-1]]
                            for player in ordering_to_group[1:-1]:
                                new_ordering.append(player)
                            ordering_to_group = new_ordering
                            for player_id in ordering_to_group:
                                if player_id != "pausing":
                                    player_to_add = ProfileInCup.objects.get(
                                        id=player_id
                                    )
                                    player_to_add.group = new_group
                                    player_to_add.save()
                                    players.append(player_to_add)
                                else:
                                    players.append("pausing")
                            new_round = Round.objects.create(
                                cup=new_group, name=f"Kolejka {round_nr}"
                            )
                            new_round2 = Round.objects.create(
                                cup=new_group,
                                name=f"Kolejka {round_nr + all_rounds - 1}",
                                match=2,
                            )
                            for match in range(len(players) // 2):
                                if players[0] == "pausing":
                                    pausing = players.pop(-1)
                                    players.remove(players[0])
                                    new_round.pausing = pausing
                                    new_round.save()
                                elif players[-1] == "pausing":
                                    pausing = players.pop(0)
                                    players.remove(players[-1])
                                    new_round.pausing = pausing
                                    new_round.save()
                                else:
                                    actual_round.append(
                                        [players.pop(0), players.pop(-1)]
                                    )
                            for match in actual_round:
                                if round_nr % 2 == 0:
                                    Match.objects.create(
                                        player1=match[0],
                                        player2=match[1],
                                        cup=new_group,
                                        round=new_round,
                                    )
                                    Match.objects.create(
                                        player1=match[1],
                                        player2=match[0],
                                        cup=new_group,
                                        round=new_round2,
                                    )
                                else:
                                    Match.objects.create(
                                        player1=match[1],
                                        player2=match[0],
                                        cup=new_group,
                                        round=new_round,
                                    )
                                    Match.objects.create(
                                        player1=match[0],
                                        player2=match[1],
                                        cup=new_group,
                                        round=new_round2,
                                    )
                            new_round.league_generated = True
                            new_round.save()
                cup.len_rounds = all_rounds
                cup.league_generated = True
                cup.save()
                messages.success(request, "Faza grupowa wygenerowana.")
                return HttpResponseRedirect("/cup/dashboard/{}/".format(cup.id))
            else:
                if not cup.cupgenerated:
                    groups = Cup.objects.filter(groupanothercup=cup)
                    cup = Cup.objects.get(id=cup_id)
                    for group in groups:
                        players = ProfileInCup.objects.filter(group=group).order_by(
                            "-points"
                        )[:2]
                        for player in players:
                            group.promotion.add(player)
                            group.save()
                            cup.promotion.add(player)
                            cup.save()
                    cup.cupgenerated = True
                players = list(cup.promotion.all())
                shuffle(players)
                cup.save()
                new_round = Round.objects.create(cup=cup)
                match_not_played = Match_not_played(cup)
                if match_not_played:
                    messages.error(
                        request,
                        "Nie rozegrano wszystkich meczy. Wprowadź wszystkie wyniki.",
                    )
                    return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
                else:
                    if cup.actual_round is not None:
                        finished_round = Round.objects.get(id=cup.actual_round.id)
                        for player_prom in list(finished_round.promotion.all()):
                            new_round.players.add(player_prom)
                    if cup.actual_round:
                        players = list(cup.actual_round.promotion.all())
                    if len(players) == 2:
                        new_round.name = "Finał"
                    elif len(players) == 4:
                        new_round.name = "Półfinał"
                    elif len(players) == 8:
                        new_round.name = "Ćwierćfinał"
                    elif len(players) == 16:
                        new_round.name = "1/8 Finału"
                    elif len(players) == 32:
                        new_round.name = "1/16 Finału"
                    elif len(players) == 64:
                        new_round.name = "1/32 Finału"
                    elif len(players) == 128:
                        new_round.name = "1/64 Finału"
                    for new_match in range(len(players) // 2):
                        player1 = random.choice(players)
                        players.remove(player1)
                        player2 = random.choice(players)
                        players.remove(player2)
                        match = Match.objects.create(
                            player1=player1, player2=player2, cup=cup, round=new_round
                        )
                        new_round.players.add(match.player1)
                        new_round.players.add(match.player2)
                    new_round.save()

                    cup.actual_round = new_round
                    cup.save()
                    messages.success(request, f"Wygenerowano {cup.actual_round}.")
                    return HttpResponseRedirect("/cup/dashboard/{}/".format(cup.id))
        else:
            messages.success(request, "Rozgrywki zakończone.")
            return HttpResponseRedirect("/cup/dashboard/{}/".format(cup.id))


@login_required
def enter_the_result(request, cup_id: int, match_id: int):
    """
    This function is used to enter the result of a match

    :type cup_id: int
    :param cup_id: The id of the cup
    :param match_id: The id of the match that the user is trying to enter the result for
    """
    cup = Cup.objects.get(id=cup_id)
    instance = get_object_or_404(Match, id=match_id)
    actual_round = cup.actual_round
    if cup.actual_round == instance.round or cup.league_generated:
        if request.method == "POST":
            if cup.type == "Puchar":
                match_form = MatchCupForm(data=request.POST or None, instance=instance)
            elif cup.type == "1 mecz":
                match_form = MatchLeagueForm(
                    data=request.POST or None, instance=instance
                )
            elif cup.type == "2 mecze":
                match_form = MatchLeagueForm(
                    data=request.POST or None, instance=instance
                )
            elif cup.type == "GrupyPuchar1mecz":
                if cup.cupgenerated:
                    match_form = MatchCupForm(
                        data=request.POST or None, instance=instance
                    )
                else:
                    match_form = MatchLeagueForm(
                        data=request.POST or None, instance=instance
                    )
            if match_form.is_valid():
                match_result = match_form.save(commit=False)
                match_result.finished = True
                match_result.confirmed = True
                player1 = ProfileInCup.objects.get(id=match_result.player1.id, cup=cup)
                player2 = ProfileInCup.objects.get(id=match_result.player2.id, cup=cup)
                if cup.type == "Puchar" or cup.cupgenerated:
                    if match_result.result1 > match_result.result2:
                        actual_round.promotion.add(player1)
                        actual_round.save()
                    else:
                        actual_round.promotion.add(player2)
                        actual_round.save()
                player1.goals_scored += match_result.result1
                player2.goals_scored += match_result.result2
                player2.goals_losted += match_result.result1
                player1.goals_losted += match_result.result2
                player1.goals_bilans += match_result.result1
                player1.goals_bilans -= match_result.result2
                player2.goals_bilans += match_result.result2
                player2.goals_bilans -= match_result.result1
                if match_result.result1 > match_result.result2:
                    player1.wins += 1
                    player1.points += 3
                    player2.losses += 1
                if match_result.result1 < match_result.result2:
                    player2.wins += 1
                    player2.points += 3
                    player1.losses += 1
                if match_result.result1 == match_result.result2:
                    player2.draws += 1
                    player2.points += 1
                    player1.points += 1
                    player1.draws += 1
                player1.save()
                player2.save()
                match_result.save()
                if cup.type == "Puchar" or cup.type == "GrupyPuchar1mecz":
                    if cup.actual_round:
                        if cup.actual_round.name == "Finał":
                            cup.finished = True
                            cup.save()
                messages.success(
                    request,
                    f"Wprowadzono wynik: "
                    f"{match_result.player1}[{match_result.result1}] "
                    f"vs "
                    f"[{match_result.result2}] {match_result.player2}",
                )
                return HttpResponseRedirect("/cup/dashboard/{}/".format(cup.id))
            else:
                match = Match.objects.get(id=match_id)
                match_not_played = Match_not_played(cup)
                context = {
                    "cup": cup,
                    "match": match,
                    "match_form": match_form,
                    "match_not_played": match_not_played,
                }
                if request.user.is_authenticated:
                    context.update(when_user_authenticated_add_variables_menu(request))
                return render(
                    request,
                    "enter_the_result.html",
                    context,
                )
        else:
            if cup.type == "Puchar":
                match_form = MatchCupForm()
            elif cup.type == "1 mecz":
                match_form = MatchLeagueForm()
            elif cup.type == "2 mecze":
                match_form = MatchLeagueForm()
            elif cup.type == "GrupyPuchar1mecz":
                match_form = MatchLeagueForm()
        match = Match.objects.get(id=match_id)
        matches = Match.objects.filter(cup=cup)
        match_not_played = Match_not_played(cup)
        context = {
            "cup": cup,
            "match": match,
            "match_form": match_form,
            "match_not_played": match_not_played,
        }
        if request.user.is_authenticated:
            context.update(when_user_authenticated_add_variables_menu(request))
        return render(
            request,
            "enter_the_result.html",
            context,
        )
    else:
        messages.error(
            request,
            "Nie możesz wprowadzić wyniku z innego etapu rozgrywek niż aktualny.",
        )
        return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")


@login_required
def delete_the_result(request, cup_id: int, match_id: int):
    """
    This function deletes the result of a match

    :param cup_id: The id of the cup that the match is in
    :param match_id: The id of the match that you want to delete
    """
    cup = Cup.objects.get(id=cup_id)
    actual_round = cup.actual_round
    match = Match.objects.get(id=match_id)
    if cup.actual_round == match.round or cup.league_generated:
        if cup.type == "Puchar" or cup.cupgenerated:
            if match.result1 > match.result2:
                actual_round.promotion.remove(match.player1)
                actual_round.save()
            else:
                actual_round.promotion.remove(match.player2)
                actual_round.save()
        player1 = ProfileInCup.objects.get(id=match.player1.id, cup=cup)
        player2 = ProfileInCup.objects.get(id=match.player2.id, cup=cup)
        player1.goals_scored -= match.result1
        player2.goals_scored -= match.result2
        player2.goals_losted -= match.result1
        player1.goals_losted -= match.result2
        player1.goals_bilans -= match.result1
        player1.goals_bilans += match.result2
        player2.goals_bilans -= match.result2
        player2.goals_bilans += match.result1
        if match.result1 > match.result2:
            player1.wins -= 1
            player1.points -= 3
            player2.losses -= 1
        if match.result1 < match.result2:
            player2.wins -= 1
            player2.points -= 3
            player1.losses -= 1
        if match.result1 == match.result2:
            player2.draws -= 1
            player2.points -= 1
            player1.points -= 1
            player1.draws -= 1
        player1.save()
        player2.save()
        match.save()
        messages.success(
            request,
            f"Skasowano wynik: {match.player1}[{match.result1}] vs [{match.result2}] {match.player2}",
        )
        match.finished = False
        match.confirmed = False
        match.result1 = None
        match.result2 = None
        match.save()
        if cup.type == "Puchar":
            if cup.actual_round.name == "Finał":
                cup.finished = False
                cup.save()
        return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
    else:
        messages.error(
            request, "Nie możesz wycofać wyniku z innego etapu rozgrywek niż aktualny."
        )
        return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")


@login_required
def panel(request):
    cups = (
        Cup.objects.exclude(declarations="Ręczna")
        .filter(declarations="Na zaproszenie", players=request.user)
        .exclude(archived=True)
        .order_by("-id")
    )
    context = {
        "cups": cups,
    }
    if request.user.is_authenticated:
        context.update(when_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "cups_list_online_to_join.html",
        context,
    )


@login_required
def join_the_cup(request, cup_id):
    cup = Cup.objects.get(id=cup_id)
    if request.user not in cup.players.all():
        cup.players.add(request.user)
        cup.number_of_players += 1
        cup.save()
        profile = Profile.objects.get(user=request.user)
        ProfileInCup.objects.create(
            user=request.user, name=request.user.first_name, cup=cup, team=profile.team
        )
        messages.success(request, f"Dołączyłeś do {cup.name}.")
        return HttpResponseRedirect("/cup/online/panel/")
    else:
        messages.error(request, f"Jesteś już uczestnikiem rozgrywek {cup.name}.")
        return HttpResponseRedirect("/cup/online/panel/")


@login_required
def left_the_cup(request, cup_id):
    cup = Cup.objects.get(id=cup_id)
    if cup.registration == "Otwarta":
        if request.user in cup.players.all():
            cup.players.remove(request.user)
            cup.number_of_players -= 1
            cup.save()
            profile = ProfileInCup.objects.get(user=request.user, cup=cup)
            profile.delete()
            messages.success(request, f"Zrezygnowałeś z udziału w {cup.name}.")
            return HttpResponseRedirect("/cup/online/panel/")
        else:
            messages.error(
                request,
                f"Nie ma Ciebie na liście rozgrywek {cup.name}, więc nie możesz zrezygnować.",
            )
            return HttpResponseRedirect("/cup/onlineonline/panel/")
    else:
        messages.error(
            request, "Nie można zrezygnować z rozgrywek po zamknięciu rejestracji."
        )
        return HttpResponseRedirect("/cup/onlineonline/panel/")


@login_required
def list_matches_to_enter(request):
    player = ProfileInCup.objects.filter(user=request.user)
    matches = (
        Match.objects.filter(Q(player1__in=player) | Q(player2__in=player))
        .filter(confirmed=False)
        .filter(Q(cup__declarations="Otwarta") | Q(cup__declarations="Na zaproszenie"))
    )
    context = {
        "matches": matches,
    }
    if request.user.is_authenticated:
        context.update(when_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "list_matches_to_enter.html",
        context,
    )


@login_required
def enter_the_result_home(request, match_id: int):
    """
    This function is used to enter the result of a match

    :type cup_id: int
    :param cup_id: The id of the cup
    :param match_id: The id of the match that the user is trying to enter the result for
    """
    match = Match.objects.get(id=match_id)
    cup = Cup.objects.get(id=match.cup.id)
    instance = get_object_or_404(Match, id=match_id)
    if cup.actual_round == match.round or cup.league_generated:
        if (
            match.player1.user == request.user
            and not match.finished
            or request.user == cup.author
        ):
            if request.method == "POST":
                if cup.type == "Puchar":
                    match_form = MatchCupForm(
                        data=request.POST or None, instance=instance
                    )
                elif cup.type == "1 mecz":
                    match_form = MatchLeagueForm(
                        data=request.POST or None, instance=instance
                    )
                elif cup.type == "2 mecze":
                    match_form = MatchLeagueForm(
                        data=request.POST or None, instance=instance
                    )
                if match_form.is_valid():
                    match_result = match_form.save(commit=False)
                    match_result.finished = True
                    match_result.save()

                    messages.success(
                        request,
                        f"Wprowadzono wynik: "
                        f"{match_result.player1}[{match_result.result1}] "
                        f"vs "
                        f"[{match_result.result2}] {match_result.player2}",
                    )
                    return HttpResponseRedirect("/cup/online/list_matches_to_enter/")
                else:
                    match = Match.objects.get(id=match_id)
                    matches = Match.objects.filter(cup=cup)
                    match_not_played = Match_not_played(cup)
                    context = {
                        "cup": cup,
                        "match": match,
                        "match_form": match_form,
                        "match_not_played": match_not_played,
                    }
                    if request.user.is_authenticated:
                        context.update(
                            when_user_authenticated_add_variables_menu(request)
                        )
                    return render(
                        request,
                        "enter_the_result.html",
                        context,
                    )
            else:
                if cup.type == "Puchar":
                    match_form = MatchCupForm()
                elif cup.type == "1 mecz":
                    match_form = MatchLeagueForm()
                elif cup.type == "2 mecze":
                    match_form = MatchLeagueForm()
            match = Match.objects.get(id=match_id)
            matches = Match.objects.filter(cup=cup)
            match_not_played = Match_not_played(cup)
            context = {
                "cup": cup,
                "match": match,
                "match_form": match_form,
                "match_not_played": match_not_played,
            }
            if request.user.is_authenticated:
                context.update(when_user_authenticated_add_variables_menu(request))
            return render(
                request,
                "enter_the_result.html",
                context,
            )
        else:
            messages.error(
                request,
                f"Nie jesteś gospodarzem lub mecz został już wpisany przez organizatora.",
            )
            return HttpResponseRedirect("/cup/online/list_matches_to_enter/")
    else:
        messages.error(
            request,
            "Nie możesz wprowadzić wyniku z innego etapu rozgrywek niż aktualny.",
        )
        return HttpResponseRedirect("/cup/online/list_matches_to_enter/")


@login_required
def delete_the_result_home(request, match_id: int):
    """
    This function is used to enter the result of a match

    :type cup_id: int
    :param cup_id: The id of the cup
    :param match_id: The id of the match that the user is trying to enter the result for
    """
    match = Match.objects.get(id=match_id)
    cup = Cup.objects.get(id=match.cup.id)
    if cup.actual_round == match.round or cup.league_generated:
        if match.player1.user == request.user and not match.confirmed:
            messages.success(
                request,
                f"Skasowano wynik: {match.player1}[{match.result1}] vs [{match.result2}] {match.player2}",
            )
            match.finished = False
            match.result1 = None
            match.result2 = None
            match.save()
            return HttpResponseRedirect("/cup/online/list_matches_to_enter/")
        else:
            messages.error(
                request,
                "Nie można skasować wyniku ponieważ został już zatwierdzony lub nie jesteś gospodarzem.",
            )
            return HttpResponseRedirect("/cup/online/list_matches_to_enter/")
    else:
        messages.error(
            request, "Nie możesz skasować wyniku z innego etapu rozgrywek niż aktualny."
        )
        return HttpResponseRedirect("/cup/online/list_matches_to_enter/")


@login_required
def confirm_the_result(request, match_id):
    match = Match.objects.get(id=match_id)
    cup = Cup.objects.get(id=match.cup.id)
    actual_round = cup.actual_round
    if cup.actual_round == match.round:
        if (
            match.player2.user == request.user
            and not match.confirmed
            and match.finished
        ):
            if cup.type == "Puchar" or cup.cupgenerated:
                if match.result1 > match.result2:
                    actual_round.promotion.add(match.player1)
                    actual_round.save()
                else:
                    actual_round.promotion.add(match.player2)
                    actual_round.save()

            player1 = ProfileInCup.objects.get(id=match.player1.id, cup=cup)
            player2 = ProfileInCup.objects.get(id=match.player2.id, cup=cup)
            player1.goals_scored += match.result1
            player2.goals_scored += match.result2
            player2.goals_losted += match.result1
            player1.goals_losted += match.result2
            player1.goals_bilans += match.result1
            player1.goals_bilans -= match.result2
            player2.goals_bilans += match.result2
            player2.goals_bilans -= match.result1
            if match.result1 > match.result2:
                player1.wins += 1
                player1.points += 3
                player2.losses += 1
            if match.result1 < match.result2:
                player2.wins += 1
                player2.points += 3
                player1.losses += 1
            if match.result1 == match.result2:
                player2.draws += 1
                player2.points += 1
                player1.points += 1
                player1.draws += 1
            player1.save()
            player2.save()
            match.confirmed = True
            match.save()
            if cup.type == "Puchar" or cup.type == "GrupyPuchar1mecz":
                if cup.actual_round.name == "Finał":
                    cup.finished = True
                    cup.save()
            messages.success(request, "Wynik potwierdzony.")
            return HttpResponseRedirect(f"/cup/dashboard/{cup.id}/")
        else:
            messages.error(
                request,
                "Nie można potwierdzić wyniku, ponieważ nie został jeszcze wprowadzony przez gospodarza lub nie jesteś gościem.",
            )
            return HttpResponseRedirect("/cup/online/list_matches_to_enter/")
    else:
        messages.error(
            request, "Nie możesz skasować wyniku z innego etapu rozgrywek niż aktualny."
        )
        return HttpResponseRedirect("/cup/online/list_matches_to_enter/")


@login_required
def reject_the_result(request, match_id):
    match = Match.objects.get(id=match_id)
    if match.player2.user == request.user and not match.confirmed and match.finished:
        messages.success(
            request,
            f"Odrzucono wynik: {match.player1}[{match.result1}] vs [{match.result2}] {match.player2}",
        )
        match.finished = False
        match.result1 = None
        match.result2 = None
        match.save()
        return HttpResponseRedirect("/cup/online/list_matches_to_enter/")
    else:
        messages.error(
            request,
            "Nie można odrzucić wyniku, ponieważ nie został jeszcze wprowadzony przez gospodarza lub nie jesteś gościem.",
        )
        return HttpResponseRedirect("/cup/online/list_matches_to_enter/")


@login_required
def archival_matches(request):
    player = ProfileInCup.objects.filter(user=request.user)
    matches = (
        Match.objects.filter(Q(player1__in=player) | Q(player2__in=player))
        .filter(Q(finished=True) & Q(confirmed=True))
        .order_by("-id")
    )
    matches_paginator = Paginator(matches, 20)
    page_num = request.GET.get("page")
    page = matches_paginator.get_page(page_num)
    context = {
        "matches": matches,
        "page": page,
        "count": matches_paginator.count,
    }
    if request.user.is_authenticated:
        context.update(when_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "archival_matches.html",
        context,
    )


@login_required
def archival_cups(request):
    player = ProfileInCup.objects.filter(user=request.user)
    matches = (
        Match.objects.filter(Q(player1__in=player) | Q(player2__in=player))
        .filter(Q(finished=True) & Q(confirmed=True))
        .order_by("-id")
    )
    cups = Cup.objects.filter(author=request.user, archived=True).order_by("-id")
    cups_paginator = Paginator(cups, 20)
    page_num = request.GET.get("page")
    page = cups_paginator.get_page(page_num)
    context = {
        "matches": matches,
        "cups": cups,
        "page": page,
        "count": cups_paginator.count,
    }
    if request.user.is_authenticated:
        context.update(when_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "archival_cups.html",
        context,
    )


@login_required
def archive(request, cup_id):
    cup = Cup.objects.get(id=cup_id)
    if cup.finished:
        cup.archived = True
        cup.save()
        messages.success(request, f"Zarchiwizowano rozgrywki {cup.name}")
        return HttpResponseRedirect("/cup/online/archival_cups/")
    else:
        messages.success(request, "Nie można zarchiwizować nieukończonych rozgrywek.")
        return HttpResponseRedirect("/cup/online/archival_cups/")


@login_required
def send_invite(request, cup_id, player_id):
    cup = Cup.objects.get(id=cup_id)
    from_player = cup.author
    to_player = User.objects.get(id=player_id)
    if request.user == from_player:
        if (
            len(
                Invite.objects.filter(
                    cup=cup,
                    from_player=from_player,
                    to_player=to_player,
                    status="Wysłano",
                )
            )
            < 1
        ):
            Invite.objects.create(
                cup=cup, from_player=from_player, to_player=to_player, status="Wysłano"
            )
            messages.success(
                request,
                f"Zaproszono {to_player.username} do udziału w rozgrywkach '{cup.name}'.",
            )
            return HttpResponseRedirect(f"/cup/online/{cup.id}/edit_players_online/")
        else:
            messages.error(
                request,
                f"Zaproszono już wcześniej {to_player.username} do udziału w rozgrywkach {cup.name}.",
            )
            return HttpResponseRedirect(f"/cup/online/{cup.id}/edit_players_online/")

    else:
        messages.success(
            request,
            f"Nie możesz wysłać zaproszenia jeżeli nie jesteś organizatorem rozgrywek.",
        )
        return HttpResponseRedirect(f"/cup/online/{cup.id}/edit_players_online/")


@login_required
def confirm_invite(request, cup_id):
    cup = Cup.objects.get(id=cup_id)
    to_player = User.objects.get(id=request.user.id)
    invite = Invite.objects.get(cup=cup, to_player=to_player)
    if request.user == invite.to_player:
        cup.players.add(to_player)
        cup.number_of_players += 1
        cup.save()
        profile = Profile.objects.get(user=request.user)
        ProfileInCup.objects.create(
            user=request.user, name=request.user.first_name, cup=cup, team=profile.team
        )
        invite.delete()
        messages.success(
            request,
            f"Zaproszenie zaakceptowano. Zarejestrowano Ciebie w rozgrywkach '{cup.name}'.",
        )
        return HttpResponseRedirect(f"/cup/online/panel/")
    else:
        messages.success(request, "Przyjąć zaproszenie może tylko jego adresat.")
        return HttpResponseRedirect(f"/cup/online/panel/")


@login_required
def reject_invite(request, cup_id, player_id_to_del):
    cup = Cup.objects.get(id=cup_id)
    player_to_del = User.objects.get(id=player_id_to_del)
    invite = Invite.objects.get(cup=cup, to_player=player_to_del)
    if request.user == invite.to_player or request.user == cup.author:
        invite.delete()
        messages.error(request, f"Odrzucono zaproszenie do rozgrywek {cup.name}.")
        return HttpResponseRedirect(f"/cup/online/panel/")
    else:
        messages.error(
            request, "Odrzucić zaproszenie może jego adresat lub organizator."
        )
        return HttpResponseRedirect(f"/cup/online/panel/")
