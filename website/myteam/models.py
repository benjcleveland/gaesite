from django.db import models
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField( widget=forms.PasswordInput )

# Create your models here.
