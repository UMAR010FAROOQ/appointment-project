from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
        strip=False,
        help_text=forms.PasswordInput().attrs.update({'class': 'form-control floating'}),
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        strip=False,
        widget=forms.PasswordInput,
        help_text=forms.PasswordInput().attrs.update({'class': 'form-control floating'}),
    )

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        # Additional custom password checks can be added here
        return password1
