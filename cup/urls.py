from django.urls import path
from .views import cups_list_offline, my_cups_list_online, cup_new, dashboard, edit_players, delete, del_players, \
    generate_round, close_registration, enter_the_result, delete_the_result, stats, \
    cup_list_with_open_registration_online, join_the_cup, left_the_cup, edit_players_online, list_matches_to_enter, \
    list_matches_to_confirm, enter_the_result_home, delete_the_result_home, confirm_the_result


urlpatterns = [
    path('offline/<int:user_id>/', cups_list_offline, name='cups_list_offline'),
    path('online/<int:user_id>/my', my_cups_list_online, name='my_cups_list_online'),
    path('online/cup_list_with_open_registration/', cup_list_with_open_registration_online,
         name='cup_list_with_open_registration_online'),
    path('online/list_matches_to_enter/', list_matches_to_enter, name='list_matches_to_enter'),
    path('online/list_matches_to_confirm/', list_matches_to_confirm, name='list_matches_to_confirm'),
    path('online/join_the_cup/<int:cup_id>/', join_the_cup, name='join_the_cup'),
    path('online/left_the_cup/<int:cup_id>/', left_the_cup, name='left_the_cup'),
    path('online/delete_the_result_home/<int:match_id>/', delete_the_result_home, name='delete_the_result_home'),
    path('online/enter_the_result_home/<int:match_id>/', enter_the_result_home, name='enter_the_result_home'),
    path('online/confirm_the_result/<int:match_id>/', confirm_the_result, name='confirm_the_result'),
    path('online/<int:cup_id>/edit_players_online/', edit_players_online, name='edit_players_online'),
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
