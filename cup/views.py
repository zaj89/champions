import random
from random import shuffle
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .forms import CupForm, PlayerForm, MatchCupForm, MatchLeagueForm, PlayerWithTeamForm
from .models import Cup, Player, Match, Round


def cups_list_offline(request, user_id):
    """
    It takes a request and a list of cups and returns a rendered template of cups_list.html

    :return: A rendered version of cups_list.html with the cups variable passed to the template engine.
    The view displays a list of cups
    """
    cups = Cup.objects.filter(author_id=user_id, declarations='Ręczna')
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'cups_list.html', {'cups': cups,
                                                  'last_cup_online': last_cup_online,
                                                  'last_cup_offline': last_cup_offline})
    else:
        return render(request, 'cups_list.html', {'cups': cups})


def my_cups_list_online(request, user_id):
    """
    It takes a request and a list of cups and returns a rendered template of cups_list.html

    :return: A rendered version of cups_list.html with the cups variable passed to the template engine.
    The view displays a list of cups
    """
    cups = Cup.objects.filter(author_id=user_id).exclude(declarations='Ręczna')
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'cups_list_online_my.html', {'cups': cups,
                                                            'last_cup_online': last_cup_online,
                                                            'last_cup_offline': last_cup_offline})
    else:
        return render(request, 'cups_list_online_my.html', {'cups': cups})


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
    return HttpResponseRedirect('/')


def cup_new(request):
    """
    Creates a new cup.

    :return: Redirection to the list of players.
    """
    if request.method == 'POST':
        cup_form = CupForm(data=request.POST)
        if cup_form.is_valid():
            new_cup = cup_form.save(commit=False)
            if request.user.is_authenticated:
                new_cup.author = request.user
            new_cup.save()
            messages.success(request, "Rozgrywki zostały utworzone.")
            return HttpResponseRedirect('/cup/dashboard/{}/edit_players'.format(new_cup.id))
    else:
        cup_form = CupForm()
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'cup_new.html', {'cup_form': cup_form,
                                                'last_cup_online': last_cup_online,
                                                'last_cup_offline': last_cup_offline})
    else:
        return render(request, 'cup_new.html', {'cup_form': cup_form})


def dashboard(request, cup_id: int):
    """
    This function is used to display the dashboard of a cup

    :param cup_id: The id of the cup that we want to see the dashboard of
    :return: A rendered template of dashboard.html
    """
    cup = Cup.objects.get(id=cup_id)
    matches = Match.objects.filter(cup=cup)
    match_not_played = False
    for match in list(matches):
        if match.finished:
            pass
        else:
            match_not_played = True
    match_not_confirmed = False
    for match in list(matches):
        if match.confirmed:
            pass
        else:
            match_not_played = True
    rounds = Round.objects.filter(cup=cup).order_by('match', '-id')
    players = Player.objects.filter(cup=cup).order_by('-points')
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'dashboard.html', {'cup': cup,
                                                  'matches': matches,
                                                  'match_not_played': match_not_played,
                                                  'rounds': rounds,
                                                  'players': players,
                                                  'last_cup_online': last_cup_online,
                                                  'last_cup_offline': last_cup_offline,
                                                  'match_not_confirmed': match_not_confirmed})
    else:
        return render(request, 'dashboard.html', {'cup': cup,
                                                  'matches': matches,
                                                  'match_not_played': match_not_played,
                                                  'rounds': rounds,
                                                  'players': players,
                                                  'match_not_confirmed': match_not_confirmed})


def stats(request, cup_id: int):
    """
    The view displays the cup statistics.

    :param cup_id: The id of the cup you want to see the stats of
    :return: A rendered template of the stats.html page.
    """
    cup = Cup.objects.get(id=cup_id)
    players_goals = Player.objects.filter(cup=cup).order_by('-goals_bilans')
    matches = Match.objects.filter(cup=cup)
    match_not_played = False
    for match in list(matches):
        if match.finished:
            pass
        else:
            match_not_played = True
    rounds = Round.objects.filter(cup=cup)[::-1]
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'stats.html', {'cup': cup,
                                              'matches': matches,
                                              'match_not_played': match_not_played,
                                              'rounds': rounds,
                                              'players_goals': players_goals,
                                              'last_cup_online': last_cup_online,
                                              'last_cup_offline': last_cup_offline})
    else:
        return render(request, 'stats.html', {'cup': cup,
                                              'matches': matches,
                                              'match_not_played': match_not_played,
                                              'rounds': rounds,
                                              'players_goals': players_goals,})


def edit_players(request, cup_id: int):
    """
    It renders the edit_players.html template,
    which is used to add new players to the cup.

    :param cup_id: ID of the cup we want to edit the player list
    :return: A rendered template of the edit_players.html page.
    """
    cup = Cup.objects.get(id=cup_id)
    players = Player.objects.filter(cup_id=cup_id)
    if request.method == 'POST':
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
            return HttpResponseRedirect('/cup/dashboard/{}/edit_players'.format(cup.id))
    else:
        player_form = PlayerForm()
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'edit_players.html', {'cup': cup,
                                                     'players': players,
                                                     'player_form': player_form,
                                                     'last_cup_online': last_cup_online,
                                                     'last_cup_offline': last_cup_offline})
    else:
        return render(request, 'edit_players.html', {'cup': cup,
                                                     'players': players,
                                                     'player_form': player_form,})


def edit_players_online(request, cup_id: int):
    cup = Cup.objects.get(id=cup_id)
    return render(request, 'edit_players.html', {'cup': cup})


def del_players(request, cup_id: int, player_to_del: int):
    """
    It deletes a player from the database and updates the number of players in the cup

    :param cup_id: The ID of the cup you want to edit
    :param player_to_del: The id of the player to delete
    :return: A redirect to the edit_players view.
    """
    cup = Cup.objects.get(id=cup_id)
    player_to_delete = Player.objects.get(id=player_to_del)
    player_to_delete.delete()
    cup.number_of_players -= 1
    cup.save()
    messages.success(request, f'Gracz "{player_to_delete.name}" został skasowany.')
    return HttpResponseRedirect('/cup/dashboard/{}/edit_players'.format(cup.id))


def close_registration(request, cup_id: int):
    """
    It closes the registration for the cup.

    :param cup_id: The ID of the cup that you want to close the registration for
    :return: A rendered template of the dashboard.html page.
    """
    cup = Cup.objects.get(id=cup_id)
    if cup.type == 'Puchar':
        players = list(Player.objects.filter(cup=cup))
        if len(players) == 4:
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
        cup.registration = 'Zamknięta'
        cup.save()
        messages.success(request, 'Rejestracja została zamknięta.')
        return HttpResponseRedirect(f'/cup/dashboard/{cup.id}/')

    elif cup.type == 'Grupy + Puchar':
        pass
    elif cup.type == '1 mecz':
        players = list(Player.objects.filter(cup=cup))
        shuffle(players)
        cup.registration = 'Zamknięta'
        len_players = 0
        for player in players:
            len_players += 1
            cup.players_order = str(cup.players_order) + str(player.id) + ','
        if len_players % 2 == 0:
            pass
        else:
            cup.players_order = cup.players_order + "pausing,"
        cup.save()
        messages.success(request, 'Rejestracja została zamknięta.')
        return HttpResponseRedirect(f'/cup/dashboard/{cup.id}/')

    elif cup.type == '2 mecze':
        players = list(Player.objects.filter(cup=cup))
        shuffle(players)
        cup.registration = 'Zamknięta'
        for player in players:
            cup.players_order = str(cup.players_order) + str(player.id) + ','
        cup.save()
        messages.success(request, 'Rejestracja została zamknięta.')
        return HttpResponseRedirect(f'/cup/dashboard/{cup.id}/')


def generate_round(request, cup_id: int):
    """
    Generate new round for cup

    :param cup_id: int The ID of the cup you want to generate a round for
    :return: A rendered template of the dashboard.html page.
    """
    cup = Cup.objects.get(id=cup_id)
    matches = Match.objects.filter(cup=cup)
    if cup.type == 'Puchar':
        new_round = Round.objects.create(cup=cup)
        match_not_played = False
        for match in list(matches):
            if match.finished:
                pass
            else:
                match_not_played = True
        if match_not_played:
            messages.success(request, 'Nie rozegrano wszystkich meczy. Wprowadź wszystkie wyniki.')
            return HttpResponseRedirect(f'/cup/dashboard/{cup.id}/')
        else:
            if cup.actual_round is not None:
                finished_round = Round.objects.get(id=cup.actual_round.id)
                for player_prom in list(finished_round.promotion.all()):
                    new_round.players.add(player_prom)
            if not cup.elimination_generated and cup.elimination_matches > 0:
                players = list(Player.objects.filter(cup=cup))
                new_round.name = 'Eliminacje'
                for new_match in range(cup.elimination_matches):
                    player1 = random.choice(players)
                    players.remove(player1)
                    player2 = random.choice(players)
                    players.remove(player2)
                    Match.objects.create(player1=player1, player2=player2, cup=cup, round=new_round)
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
                    players = list(Player.objects.filter(cup=cup))
                if len(players) == 2:
                    new_round.name = 'Finał'
                elif len(players) == 4:
                    new_round.name = 'Półfinał'
                elif len(players) == 8:
                    new_round.name = 'Ćwierćfinał'
                elif len(players) == 16:
                    new_round.name = '1/8 Finału'
                elif len(players) == 32:
                    new_round.name = '1/16 Finału'
                elif len(players) == 64:
                    new_round.name = '1/32 Finału'
                elif len(players) == 128:
                    new_round.name = '1/64 Finału'
                for new_match in range(len(players) // 2):
                    player1 = random.choice(players)
                    players.remove(player1)
                    player2 = random.choice(players)
                    players.remove(player2)
                    match = Match.objects.create(player1=player1, player2=player2, cup=cup, round=new_round)
                    new_round.players.add(match.player1)
                    new_round.players.add(match.player2)
                new_round.save()

            cup.actual_round = new_round
            cup.save()
            messages.success(request, f'Wygenerowano {cup.actual_round}.')
            return HttpResponseRedirect('/cup/dashboard/{}/'.format(cup.id))
    elif cup.type == "1 mecz":
        global ordering
        ordering = list(cup.players_order[:-1].split(','))
        if len(ordering) % 2 == 0:
            all_rounds = len(ordering)
        else:
            all_rounds = len(ordering) + 1
        players = []
        for player_id in ordering:
            if player_id != 'pausing':
                players.append(Player.objects.get(id=player_id))
            else:
                players.append('pausing')
        for round_nr in range(all_rounds)[1:]:
            actual_round = []
            if round_nr == 1:
                new_round = Round.objects.create(cup=cup, name=f'Kolejka {round_nr}')
                for match in range(len(players) // 2):
                    if players[0] == 'pausing':
                        pausing = players.pop(-1)
                        new_round.pausing = pausing
                        new_round.save()
                        players.remove(players[0])
                        players.remove(pausing)
                    elif players[-1] == 'pausing':
                        pausing = players[0]
                        new_round.pausing = pausing
                        new_round.save()
                        players.remove(pausing)
                        players.remove(players[-1])
                    else:
                        actual_round.append([players.pop(0), players.pop(-1)])
                for match in actual_round:
                    if round_nr % 2 == 0:
                        Match.objects.create(player1=match[0],
                                             player2=match[1],
                                             cup=cup,
                                             round=new_round)
                    else:
                        Match.objects.create(player1=match[1],
                                             player2=match[0],
                                             cup=cup,
                                             round=new_round)
            else:
                players = []
                new_ordering = [ordering[0], ordering[-1]]
                for player in ordering[1:-1]:
                    new_ordering.append(player)
                ordering = new_ordering
                for player_id in ordering:
                    if player_id != 'pausing':
                        players.append(Player.objects.get(id=player_id))
                    else:
                        players.append('pausing')
                new_round = Round.objects.create(cup=cup, name=f'Kolejka {round_nr}')
                for match in range(len(players) // 2):
                    if players[0] == 'pausing':
                        pausing = players.pop(-1)
                        players.remove(players[0])
                        new_round.pausing = pausing
                        new_round.save()
                    elif players[-1] == 'pausing':
                        pausing = players.pop(0)
                        players.remove(players[-1])
                        new_round.pausing = pausing
                        new_round.save()
                    else:
                        actual_round.append([players.pop(0), players.pop(-1)])
                for match in actual_round:
                    if round_nr % 2 == 0:
                        Match.objects.create(player1=match[0],
                                             player2=match[1],
                                             cup=cup,
                                             round=new_round)
                    else:
                        Match.objects.create(player1=match[1],
                                             player2=match[0],
                                             cup=cup,
                                             round=new_round)
        cup.len_rounds = all_rounds
        cup.league_generated = True
        cup.save()
        messages.success(request, 'Rozgrywki wygenerowane.')
        return HttpResponseRedirect('/cup/dashboard/{}/'.format(cup.id))
    elif cup.type == "2 mecze":
        ordering = list(cup.players_order[:-1].split(','))
        if len(ordering) % 2 == 0:
            all_rounds = len(ordering)
        else:
            all_rounds = (len(ordering) + 1)
        players = []
        for player_id in ordering:
            if player_id != 'pausing':
                players.append(Player.objects.get(id=player_id))
            else:
                players.append('pausing')
        for round_nr in range(all_rounds)[1:]:
            actual_round = []
            if round_nr == 1:
                new_round = Round.objects.create(cup=cup, name=f'Kolejka {round_nr}', match=1)
                new_round2 = Round.objects.create(cup=cup, name=f'Kolejka {round_nr + all_rounds - 1}', match=2)
                for match in range(len(players) // 2):
                    if players[0] == 'pausing':
                        pausing = players.pop(-1)
                        new_round.pausing = pausing
                        new_round.save()
                        new_round2.pausing = pausing
                        new_round2.save()
                        players.remove(players[0])
                        players.remove(pausing)
                    elif players[-1] == 'pausing':
                        pausing = players[0]
                        new_round.pausing = pausing
                        new_round.save()
                        new_round2.pausing = pausing
                        new_round2.save()
                        players.remove(pausing)
                        players.remove(players[-1])
                    else:
                        actual_round.append([players.pop(0), players.pop(-1)])
                for match in actual_round:
                    if round_nr % 2 == 0:
                        Match.objects.create(player1=match[0],
                                             player2=match[1],
                                             cup=cup,
                                             round=new_round)
                        Match.objects.create(player1=match[0],
                                             player2=match[1],
                                             cup=cup,
                                             round=new_round2)
                    else:
                        Match.objects.create(player1=match[1],
                                             player2=match[0],
                                             cup=cup,
                                             round=new_round)
                        Match.objects.create(player1=match[1],
                                             player2=match[0],
                                             cup=cup,
                                             round=new_round2)

            else:
                players = []
                new_ordering = [ordering[0], ordering[-1]]
                for player in ordering[1:-1]:
                    new_ordering.append(player)
                ordering = new_ordering
                for player_id in ordering:
                    if player_id != 'pausing':
                        players.append(Player.objects.get(id=player_id))
                    else:
                        players.append('pausing')
                new_round = Round.objects.create(cup=cup, name=f'Kolejka {round_nr}', match=1)
                new_round2 = Round.objects.create(cup=cup, name=f'Kolejka {round_nr + all_rounds - 1}', match=2)
                for match in range(len(players) // 2):
                    if players[0] == 'pausing':
                        pausing = players.pop(-1)
                        players.remove(players[0])
                        new_round.pausing = pausing
                        new_round.save()
                        new_round2.pausing = pausing
                        new_round2.save()
                    elif players[-1] == 'pausing':
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
                        Match.objects.create(player1=match[0],
                                             player2=match[1],
                                             cup=cup,
                                             round=new_round)
                        Match.objects.create(player1=match[0],
                                             player2=match[1],
                                             cup=cup,
                                             round=new_round2)
                    else:
                        Match.objects.create(player1=match[1],
                                             player2=match[0],
                                             cup=cup,
                                             round=new_round)
                        Match.objects.create(player1=match[1],
                                             player2=match[0],
                                             cup=cup,
                                             round=new_round2)
        cup.len_rounds = all_rounds
        cup.league_generated = True
        cup.save()
        messages.success(request, 'Rozgrywki wygenerowane.')
        return HttpResponseRedirect('/cup/dashboard/{}/'.format(cup.id))


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
    if request.method == 'POST':
        if cup.type == 'Puchar':
            match_form = MatchCupForm(data=request.POST or None, instance=instance)
        elif cup.type == '1 mecz':
            match_form = MatchLeagueForm(data=request.POST or None, instance=instance)
        elif cup.type == '2 mecze':
            match_form = MatchLeagueForm(data=request.POST or None, instance=instance)
        if match_form.is_valid():
            match_result = match_form.save(commit=False)
            match_result.finished = True
            match_result.confirmed = True
            if cup.type == 'Puchar':
                if match_result.result1 > match_result.result2:
                    actual_round.promotion.add(match_result.player1)
                    actual_round.save()
                else:
                    actual_round.promotion.add(match_result.player2)
                    actual_round.save()
            player1 = match_result.player1
            player2 = match_result.player2
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
            if cup.type == "Puchar":
                if cup.actual_round.name == 'Finał':
                    cup.finished = True
                    cup.save()
            messages.success(request, f'Wprowadzono wynik: '
                                      f'{match_result.player1}[{match_result.result1}] '
                                      f'vs '
                                      f'[{match_result.result2}] {match_result.player2}')
            return HttpResponseRedirect('/cup/dashboard/{}/'.format(cup.id))
        else:
            match = Match.objects.get(id=match_id)
            matches = Match.objects.filter(cup=cup)
            match_not_played = False
            for ifmatch in list(matches):
                if ifmatch.finished:
                    pass
                else:
                    match_not_played = True
            if request.user.is_authenticated:
                last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
                last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
                return render(request, 'enter_the_result.html', {'cup': cup,
                                                                 'match': match,
                                                                 'match_form': match_form,
                                                                 'match_not_played': match_not_played,
                                                                 'last_cup_online': last_cup_online,
                                                                 'last_cup_offline': last_cup_offline
                                                                 })
            else:
                return render(request, 'enter_the_result.html', {'cup': cup,
                                                                 'match': match,
                                                                 'match_form': match_form,
                                                                 'match_not_played': match_not_played})

    else:
        if cup.type == "Puchar":
            match_form = MatchCupForm()
        elif cup.type == "1 mecz":
            match_form = MatchLeagueForm()
        elif cup.type == "2 mecze":
            match_form = MatchLeagueForm()
    match = Match.objects.get(id=match_id)
    matches = Match.objects.filter(cup=cup)
    match_not_played = False
    for ifmatch in list(matches):
        if ifmatch.finished:
            pass
        else:
            match_not_played = True
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'enter_the_result.html', {'cup': cup,
                                                         'match': match,
                                                         'match_form': match_form,
                                                         'match_not_played': match_not_played,
                                                         'last_cup_online': last_cup_online,
                                                         'last_cup_offline': last_cup_offline})
    else:
        return render(request, 'enter_the_result.html', {'cup': cup,
                                                         'match': match,
                                                         'match_form': match_form,
                                                         'match_not_played': match_not_played})


def delete_the_result(request, cup_id: int, match_id: int):
    """
    This function deletes the result of a match

    :param cup_id: The id of the cup that the match is in
    :param match_id: The id of the match that you want to delete
    """
    cup = Cup.objects.get(id=cup_id)
    actual_round = cup.actual_round
    match = Match.objects.get(id=match_id)
    if cup.type == 'Puchar':
        if match.result1 > match.result2:
            actual_round.promotion.remove(match.player1)
            actual_round.save()
        else:
            actual_round.promotion.remove(match.player2)
            actual_round.save()
    player1 = match.player1
    player2 = match.player2
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
    messages.success(request, f'Skasowano wynik: {match.player1}[{match.result1}] vs [{match.result2}] {match.player2}')
    match.finished = False
    match.confirmed = False
    match.result1 = None
    match.result2 = None
    match.save()
    if cup.type == 'Puchar':
        if cup.actual_round.name == 'Finał':
            cup.finished = False
            cup.save()
    return HttpResponseRedirect(f'/cup/dashboard/{cup.id}/')


def cup_list_with_open_registration_online(request):
    cups = Cup.objects.filter(declarations='Otwarta')
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'cups_list_online_to_join.html', {'cups': cups,
                                                                 'last_cup_online': last_cup_online,
                                                                 'last_cup_offline': last_cup_offline
                                                                 })
    else:
        return render(request, 'cups_list_online_to_join.html', {'cups': cups,
                                                                 })


def join_the_cup(request, cup_id):
    cup = Cup.objects.get(id=cup_id)
    cup.players.add(request.user)
    cup.number_of_players += 1
    cup.save()
    Player.objects.create(user=request.user, name=request.user.first_name, cup=cup)
    messages.success(request, f"Dołączyłeś do {cup.name}.")
    return HttpResponseRedirect('/cup/online/cup_list_with_open_registration/')


def left_the_cup(request, cup_id):
    cup = Cup.objects.get(id=cup_id)
    cup.players.remove(request.user)
    cup.number_of_players -= 1
    cup.save()
    player_to_del = Player.objects.get(user=request.user)
    player_to_del.delete()
    messages.success(request, f"Zrezygnowałeś z udziału w {cup.name}.")
    return HttpResponseRedirect('/cup/online/cup_list_with_open_registration/')


def list_matches_to_enter(request):
    matches = Match.objects.all()
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'list_matches_to_enter.html', {'matches': matches,
                                                              'last_cup_online': last_cup_online,
                                                              'last_cup_offline': last_cup_offline
                                                              })
    else:
        return render(request, 'list_matches_to_enter.html', {'matches': matches})


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
    if request.method == 'POST':
        if cup.type == 'Puchar':
            match_form = MatchCupForm(data=request.POST or None, instance=instance)
        elif cup.type == '1 mecz':
            match_form = MatchLeagueForm(data=request.POST or None, instance=instance)
        elif cup.type == '2 mecze':
            match_form = MatchLeagueForm(data=request.POST or None, instance=instance)
        if match_form.is_valid():
            match_result = match_form.save(commit=False)
            match_result.finished = True
            match_result.save()

            messages.success(request, f'Wprowadzono wynik: '
                                      f'{match_result.player1}[{match_result.result1}] '
                                      f'vs '
                                      f'[{match_result.result2}] {match_result.player2}')
            return HttpResponseRedirect('/cup/online/list_matches_to_enter/')
        else:
            match = Match.objects.get(id=match_id)
            matches = Match.objects.filter(cup=cup)
            match_not_played = False
            for ifmatch in list(matches):
                if ifmatch.finished:
                    pass
                else:
                    match_not_played = True
            if request.user.is_authenticated:
                last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
                last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
                return render(request, 'enter_the_result.html', {'cup': cup,
                                                                 'match': match,
                                                                 'match_form': match_form,
                                                                 'match_not_played': match_not_played,
                                                                 'last_cup_online': last_cup_online,
                                                                 'last_cup_offline': last_cup_offline
                                                                 })
            else:
                return render(request, 'enter_the_result.html', {'cup': cup,
                                                                 'match': match,
                                                                 'match_form': match_form,
                                                                 'match_not_played': match_not_played})

    else:
        if cup.type == "Puchar":
            match_form = MatchCupForm()
        elif cup.type == "1 mecz":
            match_form = MatchLeagueForm()
        elif cup.type == "2 mecze":
            match_form = MatchLeagueForm()
    match = Match.objects.get(id=match_id)
    matches = Match.objects.filter(cup=cup)
    match_not_played = False
    for ifmatch in list(matches):
        if ifmatch.finished:
            pass
        else:
            match_not_played = True
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'enter_the_result.html', {'cup': cup,
                                                         'match': match,
                                                         'match_form': match_form,
                                                         'match_not_played': match_not_played,
                                                         'last_cup_online': last_cup_online,
                                                         'last_cup_offline': last_cup_offline})
    else:
        return render(request, 'enter_the_result.html', {'cup': cup,
                                                         'match': match,
                                                         'match_form': match_form,
                                                         'match_not_played': match_not_played})


def delete_the_result_home(request, match_id: int):
    """
    This function is used to enter the result of a match

    :type cup_id: int
    :param cup_id: The id of the cup
    :param match_id: The id of the match that the user is trying to enter the result for
    """
    match = Match.objects.get(id=match_id)
    messages.success(request, f'Skasowano wynik: {match.player1}[{match.result1}] vs [{match.result2}] {match.player2}')
    match.finished = False
    match.result1 = None
    match.result2 = None
    match.save()
    return HttpResponseRedirect('/cup/online/list_matches_to_enter/')


def confirm_the_result(request, match_id):
    match = Match.objects.get(id=match_id)
    cup = Cup.objects.get(id=match.cup.id)
    actual_round = cup.actual_round
    if cup.type == 'Puchar':
        if match.result1 > match.result2:
            actual_round.promotion.add(match.player1)
            actual_round.save()
        else:
            actual_round.promotion.add(match.player2)
            actual_round.save()
    player1 = match.player1
    player2 = match.player2
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
    if cup.type == "Puchar":
        if cup.actual_round.name == 'Finał':
            cup.finished = True
            cup.save()
    messages.success(request, "Wynik potwierdzony.")
    return HttpResponseRedirect('/cup/online/list_matches_to_enter/')


def list_matches_to_confirm(request):
    matches = Match.objects.all()
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'list_matches_to_confirm.html', {'matches': matches,
                                                                'last_cup_online': last_cup_online,
                                                                'last_cup_offline': last_cup_offline
                                                                })
    else:
        return render(request, 'list_matches_to_confirm.html', {'matches': matches})