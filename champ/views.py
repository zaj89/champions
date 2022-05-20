from django.shortcuts import render

from cup.models import Cup, Invite, Match


def when_user_authenticated_add_variables_menu(request):
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


def index(request):
    context = {}
    if request.user.is_authenticated:
        context.update(when_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "index.html",
        context,
    )


def help(request):
    context = {}
    if request.user.is_authenticated:
        context.update(when_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "help.html",
        context,
    )
