from django.urls import path
from .views import cups_list, cup_new, dashboard, edit_players, delete, del_players, generate_round, close_registration, \
    enter_the_result, delete_the_result, stats


urlpatterns = [
    path('list/', cups_list, name='cups_list'),
    path('new/', cup_new, name='cup_new'),
    path('dashboard/<int:cup_id>/', dashboard, name='dashboard'),
    path('dashboard/<int:cup_id>/stats', stats, name='stats'),
    path('dashboard/<int:cup_id>/enter_the_result/<int:match_id>/', enter_the_result, name='enter_the_result'),
    path('dashboard/<int:cup_id>/delete_the_result/<int:match_id>/', delete_the_result, name='delete_the_result'),
    path('dashboard/<int:cup_id>/delete/', delete, name='delete'),
    path('dashboard/<int:cup_id>/edit_players/', edit_players, name='edit_players'),
    path('dashboard/<int:cup_id>/generate_round/', generate_round, name='generate_round'),
    path('dashboard/<int:cup_id>/close_registration/', close_registration, name='close_registration'),
    path('dashboard/<int:cup_id>/del_players/<int:player_to_del>', del_players, name='del_players'),
]
