from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


# The Player class is a model that contains the information about a player
class Player(models.Model):
    class Meta:
        verbose_name = _("Gracz")
        verbose_name_plural = _("Gracze")

    name = models.CharField(max_length=30, blank=False, verbose_name='nazwa gracza', default='')
    wins = models.PositiveSmallIntegerField(verbose_name='Zwycięstwa', default=0)
    draws = models.PositiveSmallIntegerField(verbose_name='Remisy', default=0)
    losses = models.PositiveSmallIntegerField(verbose_name='Porażki', default=0)
    goals_scored = models.PositiveSmallIntegerField(verbose_name='Bramki zdobyte', default=0)
    goals_losted = models.PositiveSmallIntegerField(verbose_name='Bramki stracone', default=0)
    goals_bilans = models.SmallIntegerField(verbose_name='Bilans bramek', default=0)
    points = models.SmallIntegerField(verbose_name='Punkty', default=0)
    cup = models.ForeignKey('Cup', on_delete=models.CASCADE, related_name='cup', default='')
    group = models.ForeignKey('Cup', on_delete=models.CASCADE, related_name='group', default='', null=True)
    team = models.CharField(max_length=30, blank=True, verbose_name='Drużyna', default='', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', null=True)

    def clean(self):
        if len(str(self.name)) > 30:
            raise ValidationError("Maksymalna długość nazwy gracza to 30 znaków.")

    def __str__(self):
        return self.name


# This is a class that defines a Match object
class Match(models.Model):
    class Meta:
        verbose_name = _("Mecz")
        verbose_name_plural = _("Mecze")

    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player1', verbose_name='Gracz 1')
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player2', verbose_name='Gracz 2')
    result1 = models.PositiveSmallIntegerField(verbose_name='Wynik gospodarza', default=None, null=True)
    result2 = models.PositiveSmallIntegerField(verbose_name='Wynik gościa', default=None, null=True)
    cup = models.ForeignKey('Cup', on_delete=models.CASCADE, related_name='cup_in_match', default='')
    round = models.ForeignKey('Round', on_delete=models.CASCADE, related_name='round', default='')
    finished = models.BooleanField(verbose_name="Rozegrany", default=False)
    confirmed = models.BooleanField(verbose_name='Czy potwierdzony?', default=False)

    def clean(self):
        if self.result1 == self.result2 and self.cup.type == 'Puchar':
            raise ValidationError("Mecz nie może zakończyć się remisem.")

    def __str__(self):
        return str(self.player1) + " vs " + str(self.player2)


# This is a class that defines a Cup object
class Cup(models.Model):
    class Meta:
        verbose_name = _("Puchar")
        verbose_name_plural = _("Puchary")

    name = models.CharField(max_length=50, blank=False, verbose_name='Nazwa', default='')
    number_of_players = models.PositiveSmallIntegerField(verbose_name='Liczba graczy', default=0,
                                                         validators=[MinValueValidator(4),
                                                                     MaxValueValidator(128)])
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor', related_name='author',
                               default=None, null=True)
    types = (
        ('Puchar', (
            ('Puchar', 'Puchar (min. 4 graczy)'),
        )),
        ('Liga', (
            ('1 mecz', '1 mecz (min. 4 graczy)'),
            ('2 mecze', '2 mecze (min. 4 graczy)'),
        )),
        ('Grupy i Puchar', (
            ('GrupyPuchar1mecz', 'Grupy (1 mecz) + Puchar (min. 8 graczy)'),
            ('GrupyPuchar2mecze', 'Grupy (2 mecze) + Puchar (min. 8 graczy)'),
        )),

    )
    type = models.CharField(max_length=20, choices=types, default=types[0][0],
                            verbose_name='Rodzaj')
    reg_status = (
        ('Otwarta', 'Otwarta'),
        ('Zamknięta', 'Zamknięta'),
    )
    registration = models.CharField(max_length=20, choices=reg_status, default=reg_status[0][0],
                                    verbose_name='Rejestracja')
    len_rounds = models.PositiveSmallIntegerField(verbose_name='Liczba rund', default=0)
    elimination_matches = models.PositiveSmallIntegerField(verbose_name='Liczba meczy eliminacyjnych', default=0)
    elimination_generated = models.BooleanField(verbose_name='Wygenerowano emilimacje', default=False)
    league_generated = models.BooleanField(verbose_name='Wygenerowano ligę', default=False)
    actual_round = models.ForeignKey('Round', on_delete=models.CASCADE, related_name='actual_round', default=None,
                                     null=True)
    finished = models.BooleanField(verbose_name='Zakończono rozgrywki', default=False)
    choosing_teams = models.BooleanField(verbose_name='Wybór drużyn', default=False)
    players_order = models.CharField(max_length=50, blank=False, verbose_name='Kolejność Graczy', default='')
    online = models.BooleanField(verbose_name='online?', default=False)
    declarations_status = (
        ('Offline', (
            ('Ręczna', 'Ręczna (organizator)'),
        )),
        ('Online', (
            ('Otwarta', 'Otwarta'),
            ('Na zaproszenie', 'Na zaproszenie'),
        )),
    )
    declarations = models.CharField(max_length=20, choices=declarations_status, default=declarations_status[0][0],
                                    verbose_name='Rejestracja')
    players = models.ManyToManyField(User, related_name='players')
    groupanothercup = models.ForeignKey('Cup', on_delete=models.CASCADE, related_name='group_cups', default=None,
                                        null=True)
    promotion = models.ManyToManyField(Player, related_name='promotion_group', verbose_name='Awans', blank=True)
    cupgenerated = models.BooleanField(verbose_name='Wygenerowano puchar', default=False)

    def clean(self):
        if len(str(self.name)) > 50:
            raise ValidationError("Maksymalna długość nazwy turnieju to 50 znaków.")

    def __str__(self):
        return self.name


# This is a class that defines a Round object
class Round(models.Model):
    class Meta:
        verbose_name = _("Runda")
        verbose_name_plural = _("Rundy")

    name = models.CharField(max_length=50, blank=False, verbose_name='Nazwa rundy', default='')
    cup = models.ForeignKey('Cup', on_delete=models.CASCADE, related_name='cup_in_round', default='')
    promotion = models.ManyToManyField(Player, related_name='promotion_round', verbose_name='Awans', blank=True)
    players = models.ManyToManyField(Player, related_name='players', verbose_name='Uczestnicy', blank=True)
    pausing = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Pauzuje', null=True)
    match = models.PositiveSmallIntegerField(verbose_name='Runda meczy', null=True)

    def __str__(self):
        return self.name


class Invite(models.Model):
    class Meta:
        verbose_name = _("Zaproszenie")
        verbose_name_plural = _("Zaproszenia")
    cup = models.ForeignKey('Cup', on_delete=models.CASCADE, related_name='cup_invite', null=False, blank=False)
    from_player = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Od', null=False, related_name='from_player')
    to_player = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Do', null=False, related_name='to_player')
    stat = (
        ('Wysłano', 'Wysłano'),
        ('Potwierdzono', 'Potwierdzono'),
        ('Odrzucono', 'Odrzucono'),
    )
    status = models.CharField(max_length=20, choices=stat, default=stat[0][0],
                                    verbose_name='Status')

    def __str__(self):
        return f"Zaproszenie {self.to_player.username} do rozgrywek {self.cup.name} przez {self.from_player.username}"