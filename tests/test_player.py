import pytest
from cup.models import Player, Cup


@pytest.mark.django_db
def test_create_player1():
    cup = Cup.objects.create(name='test', type='Puchar')
    Player.objects.create(name='test', cup=cup)
    assert Player.objects.count() == 1


@pytest.mark.django_db
def test_create_player2():
    cup = Cup.objects.create(name='test', type='Grupy + Puchar')
    Player.objects.create(name='test', cup=cup)
    assert Player.objects.count() == 1


@pytest.mark.django_db
def test_create_player3():
    cup = Cup.objects.create(name='test', type='1 mecz')
    Player.objects.create(name='test', cup=cup)
    assert Player.objects.count() == 1


@pytest.mark.django_db
def test_create_player4():
    cup = Cup.objects.create(name='test', type='2 mecze')
    Player.objects.create(name='test', cup=cup)
    assert Player.objects.count() == 1