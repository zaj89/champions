from django.shortcuts import render
from cup.models import Cup, Match, Invite


def index(request):
    if request.user.is_authenticated:
        matches = Match.objects.all()
        invites = Invite.objects.filter(to_player=request.user, status='Wysłano')
        matches_user_to_waiting = matches.filter(player2__user=request.user, finished=False, confirmed=False)
        matches_user_to_enter = matches.filter(player1__user=request.user, finished=False, confirmed=False)
        matches_user_to_confirm = matches.filter(player2__user=request.user, finished=True, confirmed=False)
        matches_user_sum = len(matches_user_to_confirm) + len(matches_user_to_enter) + len(matches_user_to_waiting) + len(invites)
        print(matches_user_sum)
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'index.html', {'last_cup_online': last_cup_online,
                                              'last_cup_offline': last_cup_offline,
                                              'matches_user_to_enter': matches_user_to_enter,
                                              'matches_user_to_confirm': matches_user_to_confirm,
                                              'matches_user_to_waiting': matches_user_to_waiting,
                                              'matches_user_sum': matches_user_sum,
                                              'invites': invites})
    else:
        return render(request, 'index.html')


def help(request):
    if request.user.is_authenticated:
        invites = Invite.objects.filter(to_player=request.user, status='Wysłano')
        matches = Match.objects.all()
        matches_user_to_waiting = matches.filter(player2__user=request.user, finished=False, confirmed=False)
        matches_user_to_enter = matches.filter(player1__user=request.user, finished=False, confirmed=False)
        matches_user_to_confirm = matches.filter(player2__user=request.user, finished=True, confirmed=False)
        matches_user_sum = len(matches_user_to_confirm) + len(matches_user_to_enter) + len(matches_user_to_waiting) + len(invites)
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'help.html', {'last_cup_online': last_cup_online,
                                             'last_cup_offline': last_cup_offline,
                                             'matches_user_to_enter': matches_user_to_enter,
                                             'matches_user_to_confirm': matches_user_to_confirm,
                                             'matches_user_to_waiting': matches_user_to_waiting,
                                             'matches_user_sum': matches_user_sum,
                                             'invites': invites})
    else:
        return render(request, 'help.html')