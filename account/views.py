from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from account.models import Profile
from champ.functions import if_user_authenticated_add_variables_menu
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
        context = {"form": form}
        context.update(if_user_authenticated_add_variables_menu(request))
        return render(
            request,
            "registration/login.html",
            context,
        )


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
        user_profile_form = UserEditForm()
        return render(request, "account/register.html", {"user_form": user_form})


@login_required
def edit(request):
    profile = Profile.objects.get(user=request.user)
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
    context = {"user_form": user_form,
               "profile_form": profile_form,}
    context.update(if_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "account/edit.html",
        context,
    )


@login_required
def profile(request, user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)
    context = {
            "user": user,
            "profile": profile,
        }
    context.update(if_user_authenticated_add_variables_menu(request))
    return render(
        request,
        "account/profile.html",
        context,
    )
