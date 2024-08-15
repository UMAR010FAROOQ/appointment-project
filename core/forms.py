from django import forms
from authentication.models import CustomUser

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'gender', 'email', 'profile_image']

    def __init__(self, *args, **kwargs):
        super(UserProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['email'].disabled = True  # Email should be read-only
        self.fields['gender'].required = True

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image', False)
        if image:
            if image.size > 2 * 1024 * 1024:  # 4MB limit
                raise forms.ValidationError("Image file too large must be less than 2MB")
            return image
        return None
