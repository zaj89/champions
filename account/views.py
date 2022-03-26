from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login

from cup.models import Cup
from .forms import LoginForm, UserRegistrationForm, UserEditForm


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse("Uwierzytelnienie zakończyło się powodzeniem.")
                else:
                    return HttpResponse('Konto jest zablokowane.')
            else:
                return HttpResponse('Nieprawidłowe dane uwierzytelniające.')
    else:
        form = LoginForm()
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'account/login.html', {'form': form,
                                                      'last_cup_online': last_cup_online,
                                                      'last_cup_offline': last_cup_offline
                                                      })
    else:
        return render(request, 'account/login.html', {'form': form})


def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
        return render(request, 'account/register.html', {'user_form': user_form})


@login_required
def edit(request):
    if request.method =='POST':
        user_form = UserEditForm(instance=request.user.profile, data=request.POST)
        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
    return render(request, 'account/edit.html', {'user_form': user_form})


@login_required
def profile(request, user_id):
    user = User.objects.get(id=user_id)
    if request.user.is_authenticated:
        last_cup_online = Cup.objects.filter(author_id=request.user.id).exclude(declarations='Ręczna').last()
        last_cup_offline = Cup.objects.filter(author_id=request.user.id, declarations='Ręczna').last()
        return render(request, 'account/profile.html', {'user': user,
                                                        'last_cup_online': last_cup_online,
                                                        'last_cup_offline': last_cup_offline})
    else:
        return render(request, 'account/profile.html', {'user': user})