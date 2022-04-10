from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from cup.models import Cup


class Profile(models.Model):
    class Meta:
        verbose_name = _("Profil")
        verbose_name_plural = _("Profile")
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    team = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username


class ProfileInCup(models.Model):
    class Meta:
        verbose_name = _("ProfileInCup")
        verbose_name_plural = _("ProfileInCups")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_in_profile_cup')
    team = models.CharField(max_length=20)
    cup = models.ForeignKey(Cup, on_delete=models.CASCADE, related_name='cup_in_profile_cup')
    wins = models.PositiveSmallIntegerField(verbose_name='Zwycięstwa', default=0)
    draws = models.PositiveSmallIntegerField(verbose_name='Remisy', default=0)
    losses = models.PositiveSmallIntegerField(verbose_name='Porażki', default=0)
    goals_scored = models.PositiveSmallIntegerField(verbose_name='Bramki zdobyte', default=0)
    goals_losted = models.PositiveSmallIntegerField(verbose_name='Bramki stracone', default=0)
    goals_bilans = models.SmallIntegerField(verbose_name='Bilans bramek', default=0)
    points = models.SmallIntegerField(verbose_name='Punkty', default=0)

    def __str__(self):
        return self.user.username + self.cup.name