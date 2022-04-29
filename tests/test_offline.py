import pytest
from cup.models import Cup


@pytest.mark.django_db
def test_create_cup1():
    Cup.objects.create(name='test', type='Puchar')
    assert Cup.objects.count() == 1
