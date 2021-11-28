from django import forms
from .models import User, Club
from django.core.validators import RegexValidator


class LogInForm(forms.Form):
    email = forms.CharField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


# This user model is inspried by the one written in clucker
class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',
                  'bio', 'chess_exp', 'personal_statement']
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

    def save(self):
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
        widgets = {'bio': forms.Textarea(), 'personal_statement': forms.Textarea()}

class CreateClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'location', 'description']
        widgets = {'description': forms.Textarea()}

    def save(self, user):
        super().save(commit=False)
        club = Club.objects.create(
            name = self.cleaned_data.get('name'),
            location = self.cleaned_data.get('location'),
            description = self.cleaned_data.get('description'),
            owner = user,
        )
        return club
