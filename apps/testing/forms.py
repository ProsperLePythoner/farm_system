"""Simple form used by the authenticated testing utilities."""

from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(
        max_length=100,
        label="Your name"
    )