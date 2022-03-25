from django.shortcuts import render
from cup.models import Cup


def index(request):
    last_cup = Cup.objects.last()
    return render(request, 'index.html', {'last_cup': last_cup})