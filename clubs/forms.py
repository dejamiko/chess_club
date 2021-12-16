from django import forms
from django.forms.fields import DateField, TimeField, CharField
from .models import User, Club, Tournament
from django.core.validators import RegexValidator
from datetime import datetime
from django.utils.timezone import make_aware


class LogInForm(forms.Form):
    email = forms.CharField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


# This user model is inspired by the one written in clucker
class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',
                  'bio', 'chess_exp', 'personal_statement']
        labels = {
            'chess_exp': ('Chess experience'),
        }
        widgets = {'bio': forms.Textarea(), 'personal_statement': forms.Textarea()}

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
        )
        ]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self, **kwargs):
        super().save(commit=False)
        user = User.objects.create_user(
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            bio=self.cleaned_data.get('bio'),
            chess_exp=self.cleaned_data.get('chess_exp'),
            personal_statement=self.cleaned_data.get('personal_statement'),
            password=self.cleaned_data.get('new_password'),
        )
        return user


class EditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',
                  'bio', 'chess_exp', 'personal_statement']
        labels = {
            'chess_exp': ('Chess experience'),
        }
        widgets = {'bio': forms.Textarea(), 'personal_statement': forms.Textarea()}


class CreateClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'location', 'description']
        widgets = {'description': forms.Textarea()}

    def save(self, user):
        super().save(commit=False)
        club = Club.objects.create(
            name=self.cleaned_data.get('name'),
            location=self.cleaned_data.get('location'),
            description=self.cleaned_data.get('description'),
            owner=user,
        )
        return club


def _generate_officer_tuples(club, current_user):
    tuple_list = []
    for officer in club.get_officers():
        if officer != current_user:
            tuple_list.append((officer, officer.full_name))
    return tuple_list


class CreateTournamentForm(forms.ModelForm):
    def __init__(self, post=None, club=None, current_user=None, *args, **kwargs):
        if post:
            post = post.copy()
            temp_coorganisers = []
            for coorganiser in post.getlist("coorganisers"):
                temp_coorganisers.append(User.objects.get(email=coorganiser))
            post.setlist("coorganisers", temp_coorganisers)
            super(CreateTournamentForm, self).__init__(post, *args, **kwargs)
        else:
            super(CreateTournamentForm, self).__init__(*args, **kwargs)
        if club and current_user:
            self.fields["coorganisers"].choices = _generate_officer_tuples(club, current_user)

    deadline_date = DateField()
    deadline_date.widget = forms.TextInput(attrs={"type": "date"})
    deadline_time = TimeField()
    deadline_time.widget = forms.TextInput(attrs={"type": "time"})

    class Meta:
        model = Tournament
        fields = ["name", "description", "coorganisers"]
        widgets = {"description": forms.Textarea(), "coorganisers": forms.SelectMultiple()}
        help_texts = {"coorganisers": "Hold Ctrl/⌘ to select multiple"}

    def save(self, user, club):
        super().save(commit=False)
        tournament = Tournament.objects.create(
            club=Club.objects.get(id=club),
            name=self.cleaned_data.get("name"),
            description=self.cleaned_data.get("description"),
            organiser=user,
            deadline=make_aware(
                datetime.combine(self.cleaned_data.get("deadline_date"), self.cleaned_data.get("deadline_time")))
        )
        tournament.coorganisers.set(self.cleaned_data.get("coorganisers"))
        tournament.save()
        return tournament

#
# class ClubApplicationForm(forms.ModelForm):
#     class Meta:
#         model = ClubApplication
#         fields = ['status']
