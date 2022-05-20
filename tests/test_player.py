import pytest

from account.models import ProfileInCup
from cup.models import Cup


@pytest.mark.django_db
def test_create_player1():
    cup = Cup.objects.create(name="test", type="Puchar")
    ProfileInCup.objects.create(name="test", cup=cup)
    assert ProfileInCup.objects.count() == 1


@pytest.mark.django_db
def test_create_player2():
    cup = Cup.objects.create(name="test", type="Grupy + Puchar")
    ProfileInCup.objects.create(name="test", cup=cup)
    assert ProfileInCup.objects.count() == 1


@pytest.mark.django_db
def test_create_player3():
    cup = Cup.objects.create(name="test", type="1 mecz")
    ProfileInCup.objects.create(name="test", cup=cup)
    assert ProfileInCup.objects.count() == 1


@pytest.mark.django_db
def test_create_player4():
    cup = Cup.objects.create(name="test", type="2 mecze")
    ProfileInCup.objects.create(name="test", cup=cup)
    assert ProfileInCup.objects.count() == 1


@pytest.mark.django_db
def test_goal_bilans():
    cup = Cup.objects.create(name="test", type="2 mecze")
    player = ProfileInCup.objects.create(name="test", cup=cup)
    player.goals_scored += 3
    player.goals_losted += 1
    player.goals_bilans = player.goals_scored - player.goals_losted
    assert player.goals_bilans == 2
