from django import forms
from .models import Cup, Player, Match


# The CupForm class is a ModelForm that is used to create a new cup.
class CupForm(forms.ModelForm):
    class Meta:
        model = Cup
        fields = ('name', 'type', 'choosing_teams')


# This class is a ModelForm that is used to create a new PlayerWithTeam object.
class PlayerWithTeamForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('name', 'team',)


# The PlayerForm class is a ModelForm class that is used to create a form that can be used to create a new Player object
class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('name',)


# This is the form that will be used to enter the match result.
class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ('result1', 'result2')
