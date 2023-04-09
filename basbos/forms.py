from django import forms
from .utlize.utlize import password_validator


class CustomUserForm(forms.ModelForm):
    def clean(self):
        # validate password
        pas = self.cleaned_data['password']
        error_message = password_validator(pas)
        if error_message:
            raise forms.ValidationError(error_message, code='invalid')

        return self.cleaned_data
