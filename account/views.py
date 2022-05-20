from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from account.models import Profile
from cup.models import Cup, Invite, Match

from .forms import LoginForm, ProfileForm, UserEditForm


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd["username"], password=cd["password"])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse("Uwierzytelnienie zakończyło się powodzeniem.")
                else:
                    return HttpResponse("Konto jest zablokowane.")
            else:
                return HttpResponse("Nieprawidłowe dane uwierzytelniające.")
    else:
        form = LoginForm()
    if request.user.is_authenticated:
        matches = Match.objects.all()
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
        return render(
            request,
            "account/login.html",
            {
                "form": form,
                "last_cup_online": last_cup_online,
                "last_cup_offline": last_cup_offline,
                "matches_user_to_enter": matches_user_to_enter,
                "matches_user_to_confirm": matches_user_to_confirm,
                "matches_user_to_waiting": matches_user_to_waiting,
                "matches_user_sum": matches_user_sum,
            },
        )
    else:
        return render(request, "account/login.html", {"form": form})


def register(request):
    if request.method == "POST":
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.save()
            Profile.objects.create(user=new_user)
            messages.success(request, "Konto zostało utworzone. Możesz się zalogować.")
            return HttpResponseRedirect("/account/login/")
        else:
            return render(request, "account/register.html", {"user_form": user_form})
    else:
        user_form = UserCreationForm()
        return render(request, "account/register.html", {"user_form": user_form})


@login_required
def edit(request):
    profile = Profile.objects.get(user=request.user)
    invites = Invite.objects.filter(to_player=request.user, status="Wysłano")
    matches = Match.objects.all()
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
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileForm(instance=profile, data=request.POST)
        if user_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Dane konta został zaktualizowane.")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    return render(
        request,
        "account/edit.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "matches_user_to_enter": matches_user_to_enter,
            "matches_user_to_confirm": matches_user_to_confirm,
            "matches_user_to_waiting": matches_user_to_waiting,
            "matches_user_sum": matches_user_sum,
            "invites": invites,
        },
    )


@login_required
def profile(request, user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)
    matches = Match.objects.all()
    invites = Invite.objects.filter(to_player=request.user, status="Wysłano")
    if request.user.is_authenticated:
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
        return render(
            request,
            "account/profile.html",
            {
                "user": user,
                "profile": profile,
                "last_cup_online": last_cup_online,
                "last_cup_offline": last_cup_offline,
                "matches_user_to_enter": matches_user_to_enter,
                "matches_user_to_confirm": matches_user_to_confirm,
                "matches_user_to_waiting": matches_user_to_waiting,
                "matches_user_sum": matches_user_sum,
                "invites": invites,
            },
        )
    else:
        return render(request, "account/profile.html", {"user": user})
