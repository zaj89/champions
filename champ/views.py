from django.shortcuts import render
from cup.models import Cup
from django.contrib.auth.models import User


def index(request):
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'index.html', {'last_cup_online': last_cup_online,
                                              'last_cup_offline': last_cup_offline})
    else:
        return render(request, 'index.html')
