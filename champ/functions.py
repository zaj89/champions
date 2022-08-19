from django.contrib import messages
from django.http import HttpResponseRedirect
from account.models import ProfileInCup, Profile
from cup.models import Cup, Invite, Match


def if_match_in_cup_not_played(cup):
    matches_in_cup = Match.objects.filter(cup=cup)
    match_in_cup_not_played = False
    for match in list(matches_in_cup):
        if match.finished:
            pass
        else:
            match_in_cup_not_played = True
    return {"match_in_cup_not_played": match_in_cup_not_played}


def if_match_not_confirmed(cup):
    match_not_confirmed = False
    matches = Match.objects.filter(cup=cup)
    for match in list(matches):
        if match.confirmed:
            pass
        else:
            match_not_confirmed = True
    return match_not_confirmed


def if_match_in_groups_not_played(cup):
    matches_in_groups = Match.objects.filter(cup__groupanothercup=cup)
    match_in_groups_not_played = False
    for match in list(matches_in_groups):
        if match.finished:
            pass
        else:
            match_in_groups_not_played = True
    return match_in_groups_not_played


def if_match_not_played(cup):
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


def if_user_authenticated_add_variables_menu(request):
    if request.user.is_authenticated:
        matches = Match.objects.all()
        invites = Invite.objects.filter(to_player=request.user, status="Wysłano")
        matches_user_to_waiting = matches.filter(
            player2__user=request.user, finished=False, confirmed=False
        )
        matches_user_to_enter = matches.filter(
            player1__user=request.user, finished=False, confirmed=False
        )
        matches_user_to_confirm = matches.filter(
            player2__user=request.user, finished=True, confirmed=False
        )
        matches_user_sum = (
            len(matches_user_to_confirm)
            + len(matches_user_to_enter)
            + len(matches_user_to_waiting)
            + len(invites)
        )
        last_cup_online = (
            Cup.objects.filter(author_id=request.user.id)
            .exclude(declarations="Ręczna")
            .exclude(archived=True)
            .last()
        )
        last_cup_offline = (
            Cup.objects.filter(author_id=request.user.id, declarations="Ręczna")
            .exclude(archived=True)
            .last()
        )
        return {
            "last_cup_online": last_cup_online,
            "last_cup_offline": last_cup_offline,
            "matches_user_to_enter": matches_user_to_enter,
            "matches_user_to_confirm": matches_user_to_confirm,
            "matches_user_to_waiting": matches_user_to_waiting,
            "matches_user_sum": matches_user_sum,
            "invites": invites,
        }
    else:
        return {}


def assign_teams_from_profiles_to_profiles_in_cup(players):
    for player in players:
        profile = Profile.objects.get(user=player.user)
        player.team = profile.team
        player.save()


def calculate_len_group(request, cup, players):
    if len(players) < 4 or len(players) > 256:
        messages.success(
            request,
            "W wybranym trybie rozgrywek zarejestrowanych musi być najmniej 4 graczy i nie więcej niż 256",
        )
        return HttpResponseRedirect("/cup/dashboard/{}/edit_players".format(cup.id))
    else:
        lengroup = {
            range(128, 257): 32,
            range(64, 128): 16,
            range(32, 64): 8,
            range(16, 32): 4,
            range(4, 16): 2,
        }
        return lengroup[len(players)]


def calculate_len_rounds(request, cup, players):
    if len(players) < 4:
        messages.success(
            request,
            "W wybranym trybie rozgrywek zarejestrowanych musi być minimum 4 graczy.",
        )
        return HttpResponseRedirect("/cup/dashboard/{}/edit_players".format(cup.id))
    else:
        lenround = {
            range(128, 257): 32,
            range(64, 128): 16,
            range(32, 64): 8,
            range(16, 32): 4,
            range(4, 16): 2,
        }
        numbers_to_calculate_matches_elimination = {
            range(5, 8): 4,
            range(9, 16): 8,
            range(17, 32): 16,
            range(33, 64): 32,
            range(65, 120): 64,
        }
        len_rounds = None
        for key in lenround:
            if len(players) in key:
                len_rounds = lenround[key]
        number_to_calc = None
        for key in numbers_to_calculate_matches_elimination:
            if len(players) in key:
                number_to_calc = numbers_to_calculate_matches_elimination[key]
        if len_rounds != len(players):
            cup.elimination_matches = len(players) - number_to_calc
        cup.len_rounds = len_rounds
        cup.registration = "Zamknięta"
        cup.save()
        return len_rounds


def round_name(players, new_round):
    round_names = {
        2: "Finał",
        4: "Półfinał",
        8: "Ćwierćfinał",
        16: "1/8 Finału",
        32: "1/16 Finału",
        64: "1/32 Finału",
        128: "1/64 Finału"
    }
    new_round.name = round_names[len(players)]


def assign_stats_to_players(cup, match, actual_round):
    player1 = ProfileInCup.objects.get(id=match.player1.id, cup=cup)
    player2 = ProfileInCup.objects.get(id=match.player2.id, cup=cup)
    if cup.type == "Puchar" or cup.cupgenerated:
        if match.result1 > match.result2:
            actual_round.promotion.add(player1)
            actual_round.save()
        else:
            actual_round.promotion.add(player2)
            actual_round.save()
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
