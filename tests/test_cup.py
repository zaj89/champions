import pytest
from django.contrib.auth.models import User

from account.models import Profile
from cup.models import Cup
from cup.views import delete


@pytest.fixture
def create_user():
    user = User.objects.create(username="test", password="test")
    yield user


@pytest.fixture
def create_profile():
    profile = Profile.objects.create(username="test", password="test")
    yield profile


@pytest.fixture
def create_cup(create_user):
    cup = Cup.objects.create(name='test', type='Puchar', author=create_user, choosing_teams=True)
    yield cup


@pytest.mark.django_db
def test_create_cup1(create_user):
    Cup.objects.create(name='test', type='Puchar', author=create_user, choosing_teams=True)
    assert Cup.objects.count() == 1


@pytest.mark.django_db
def test_create_cup2(create_user):
    Cup.objects.create(name='test', type='Puchar', author=create_user, choosing_teams=False)
    assert Cup.objects.count() == 1


@pytest.mark.django_db
def test_create_cup3(create_user):
    Cup.objects.create(name='test', type='GrupyPuchar1mecz', author=create_user, choosing_teams=True)
    assert Cup.objects.count() == 1



@pytest.mark.django_db
def test_create_cup4(create_user):
    Cup.objects.create(name='test', type='GrupyPuchar1mecz', author=create_user, choosing_teams=False)
    assert Cup.objects.count() == 1



@pytest.mark.django_db
def test_create_cup5(create_user):
    Cup.objects.create(name='test', type='GrupyPuchar2mecze', author=create_user, choosing_teams=True)
    assert Cup.objects.count() == 1



@pytest.mark.django_db
def test_create_cup6(create_user):
    Cup.objects.create(name='test', type='GrupyPuchar2mecze', author=create_user, choosing_teams=False)
    assert Cup.objects.count() == 1


@pytest.mark.django_db
def test_create_cup7(create_user):
    Cup.objects.create(name='test', type='1 mecz', author=create_user, choosing_teams=True)
    assert Cup.objects.count() == 1



@pytest.mark.django_db
def test_create_cup8(create_user):
    Cup.objects.create(name='test', type='1 mecz', author=create_user, choosing_teams=False)
    assert Cup.objects.count() == 1


@pytest.mark.django_db
def test_create_cup9(create_user):
    Cup.objects.create(name='test', type='2 mecze', author=create_user, choosing_teams=True)
    assert Cup.objects.count() == 1


@pytest.mark.django_db
def test_create_cup10(create_user):
    Cup.objects.create(name='test', type='2 mecze', author=create_user, choosing_teams=False)
    assert Cup.objects.count() == 1



@pytest.mark.django_db
def test_delete_cup(create_cup):
    cup_to_del = create_cup
    assert Cup.objects.count() == 1
    cup_to_del.delete()
    assert Cup.objects.count() == 0

