from django.shortcuts import render
from .functions import if_user_authenticated_add_variables_menu


def index(request):
    context = {}
    if request.user.is_authenticated:
        context.update(if_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "index.html",
        context,
    )


def help(request):
    context = {}
    if request.user.is_authenticated:
        context.update(if_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "help.html",
        context,
    )
