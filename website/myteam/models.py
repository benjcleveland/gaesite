from django.db import models
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField( widget=forms.PasswordInput )

class googLoginForm(forms.Form):

    team_cowboy_username = forms.CharField()
    team_cowboy_password = forms.CharField( widget=forms.PasswordInput )

    google_username = forms.CharField()
    google_password = forms.CharField( widget=forms.PasswordInput )

# Create your models here.
