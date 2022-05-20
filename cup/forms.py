from django import forms

from account.models import ProfileInCup

from .models import Cup, Match


# The CupForm class is a ModelForm that is used to create a new cup.
class CupForm(forms.ModelForm):
    class Meta:
        model = Cup
        fields = ("name", "type", "choosing_teams", "declarations")

    def clean_cup(self):
        if len(str(self.cleaned_data["name"])) > 50:
            raise forms.ValidationError(
                "Maksymalna długość nazwy turnieju to 50 znaków."
            )


# This class is a ModelForm that is used to create a new PlayerWithTeam object.
class PlayerWithTeamForm(forms.ModelForm):
    class Meta:
        model = ProfileInCup
        fields = (
            "name",
            "team",
        )


# The PlayerForm class is a ModelForm class that is used to create a form that can be used to create a new Player object
class PlayerForm(forms.ModelForm):
    class Meta:
        model = ProfileInCup
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"autofocus": "True"})

    def clean_player(self):
        if len(str(self.cleaned_data["name"])) > 30:
            raise forms.ValidationError("Maksymalna długość nazwy gracza to 30 znaków.")


# This is the form that will be used to enter the match result.
class MatchCupForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ("result1", "result2")

    def clean_match(self):
        if self.cleaned_data["result1"] == self.cleaned_data["result2"]:
            raise forms.ValidationError("Mecz nie może zakończyć się remisem.")


# This is the form that will be used to enter the match result.
class MatchLeagueForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ("result1", "result2")
