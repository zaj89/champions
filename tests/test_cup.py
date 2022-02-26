import pytest
from cup.models import Cup


@pytest.mark.django_db
def test_create_cup1():
    Cup.objects.create(name='test', type='Puchar')
    assert Cup.objects.count() == 1


@pytest.mark.django_db
def test_create_cup2():
    Cup.objects.create(name='test', type='Grupy + Puchar')
    assert Cup.objects.count() == 1


@pytest.mark.django_db
def test_create_cup3():
    Cup.objects.create(name='test', type='1 mecz')
    assert Cup.objects.count() == 1


@pytest.mark.django_db
def test_create_cup4():
    Cup.objects.create(name='test', type='2 mecze')
    assert Cup.objects.count() == 1


@pytest.mark.django_db
def test_create_cup5():
    assert Cup.objects.count() == 0