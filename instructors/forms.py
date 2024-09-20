from django import forms
from authentication.models import CustomUser, InstructorProfile
from core.models import Service
from instructors.models import Education, AvailableTimeSlot


class AvailableTimeSlotForm(forms.ModelForm):
    class Meta:
        model = AvailableTimeSlot
        fields = ['day_of_week', 'start_time', 'end_time', 'is_available']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            self.add_error('start_time', 'Start time must be before end time.')

        return cleaned_data    


class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'gender', 'profile_image', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image', False)
        if image:
            if image.size > 2 * 1024 * 1024:  # 2MB limit
                raise forms.ValidationError("Image file too large, must be less than 2MB.")
            return image
        return None

class InstructorProfileUpdateForm(forms.ModelForm):
    service = forms.ModelChoiceField(queryset=Service.objects.all(), required=True)

    class Meta:
        model = InstructorProfile
        fields = ['city', 'service']

    def __init__(self, *args, **kwargs):
        super(InstructorProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.all()

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['speciality', 'minicost', 'maxcost', 'perhpur', 'aboutme']

    def clean_minicost(self):
        minicost = self.cleaned_data.get('minicost')
        return minicost if minicost else None

    def clean_maxcost(self):
        maxcost = self.cleaned_data.get('maxcost')
        return maxcost if maxcost else None

    # def clean_end_date(self):
    #     start_date = self.cleaned_data.get('start_date')
    #     end_date = self.cleaned_data.get('end_date')
    #     if start_date and end_date and start_date > end_date:
    #         raise forms.ValidationError("End date should be greater than start date.")
    #     return end_date
