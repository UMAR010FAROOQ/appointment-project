from django.shortcuts import render
from .decorators import instructor_required
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from instructors.models import InstructorPasswordChange, Education
from django.contrib.auth.forms import PasswordChangeForm
from authentication.models import InstructorProfile, CustomUser
from .forms import InstructorProfileUpdateForm, CustomUserUpdateForm, EducationForm
from core.models import Service

@instructor_required
def DashPage(request):
    return render(request, 'instructors/index.html') 


def AppointmentRequest(request):
    return render(request, 'instructors/appointment-request.html') 



def InstructorAppointments(request):
    return render(request, 'instructors/instructor-appointments.html') 



def AvailableTimings(request):
    return render(request, 'instructors/available-timings.html') 



@login_required
def InstructorProfileSettings(request):
    instructor = InstructorProfile.objects.get(user=request.user)
    user = request.user

    try:
        education = Education.objects.get(instructor=instructor)
    except Education.DoesNotExist:
        education = None

    # Initialize the forms before handling POST
    user_form = CustomUserUpdateForm(instance=user)
    profile_form = InstructorProfileUpdateForm(instance=instructor)

    # Handling the date fields for proper display
    if education:
        education_data = {
            'institution_name': education.institution_name,
            'course': education.course,
            'start_date': education.start_date.strftime('%Y-%m-%d') if education.start_date else '',
            'end_date': education.end_date.strftime('%Y-%m-%d') if education.end_date else '',
            'marks': education.marks,
            'description': education.description,
        }
        education_form = EducationForm(initial=education_data, instance=education)
    else:
        education_form = EducationForm()

    if request.method == 'POST':
        if 'first_name' in request.POST:  # Personal information form submission
            user_form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
            profile_form = InstructorProfileUpdateForm(request.POST, request.FILES, instance=instructor)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your personal information has been updated successfully!', extra_tags='success')
            else:
                for form in [user_form, profile_form]:
                    for field, errors in form.errors.items():
                        for error in errors:
                            print(f"Error in {field}: {error}")
                            messages.error(request, f"{field.capitalize()}: {error}", extra_tags='danger')
                messages.error(request, 'Please correct the errors in your personal information.', extra_tags='danger')

        elif 'institution_name' in request.POST:  # Education form submission
            education_form = EducationForm(request.POST, instance=education)
            if education_form.is_valid():
                education = education_form.save(commit=False)
                education.instructor = instructor
                education.save()
                messages.success(request, 'Your education details have been updated successfully!', extra_tags='success')
            else:
                for field, errors in education_form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"{field.capitalize()}: {error}", extra_tags='danger')
                messages.error(request, 'Please correct the errors in your education details.', extra_tags='danger')

    return render(request, 'instructors/instructor-profile-settings.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'education_form': education_form,
        'user': user,
        'services': Service.objects.all(),
    })




@login_required
def InstructorChangePassword(request):
    user = request.user
    last_change = InstructorPasswordChange.objects.filter(user=user).order_by('-timestamp').first()

    # Check if the user has changed their password in the last 24 hours
    if last_change:
        time_since_last_change = timezone.now() - last_change.timestamp
        if time_since_last_change < timedelta(hours=24):
            remaining_time = timedelta(hours=24) - time_since_last_change
            remaining_seconds = int(remaining_time.total_seconds())
            hours, remainder = divmod(remaining_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Check session to prevent redirect loop
            if not request.session.get('password_redirected'):
                messages.error(request, f"You can change your password again in {hours} hours, {minutes} minutes, and {seconds} seconds.", extra_tags='danger')
                request.session['password_redirected'] = True
                return redirect('instructors:InstructorChangePassword')

    # Clear session variable if user accesses the page without restriction
    request.session['password_redirected'] = False

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            # Save the timestamp of the password change
            InstructorPasswordChange.objects.create(user=user)
            # Update the session with the new password
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!', extra_tags='success')
            return redirect('instructors:InstructorChangePassword')
        else:
            # Debugging information
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")  # Log errors to console or wherever you're capturing logs
                    messages.error(request, f"{field.capitalize()}: {error}", extra_tags='danger')
            messages.error(request, 'Please correct the errors below.', extra_tags='danger')
    else:
        form = PasswordChangeForm(user)

    return render(request, 'instructors/instructor-change-password.html', {'form': form})





