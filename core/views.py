from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact
from core.models import Service
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from datetime import timedelta
from core.models import PasswordChange
from django.contrib.auth.forms import PasswordChangeForm
from core.forms import UserProfileUpdateForm
from .decorators import simple_user_required
from authentication.models import InstructorProfile
from instructors.models import Education
from django.db.models import Min, Max

# @simple_user_required
def HomePage(request):
    services = Service.objects.all()
    return render(request, 'user/index.html', {'services': services})



def AboutPage(request):
    return render(request, 'user/aboutus.html') 


def ContactPage(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get('name')
        email = request.POST.get('email')
        country = request.POST.get('country')
        city = request.POST.get('city')
        service_id = request.POST.get('service')
        gender = request.POST.get('gender')
        message = request.POST.get('message')

        # Validate that all fields are present
        if not all([name, email, country, city, service_id, gender, message]):
            return JsonResponse({'success': False, 'error': 'All fields are required.'})

        # Save the data to the database
        try:
            service = Service.objects.get(id=service_id)
            contact = Contact.objects.create(
                name=name,
                email=email,
                country=country,
                city=city,
                service=service,
                gender=gender,
                message=message
            )
            contact.save()
            return JsonResponse({'success': True})
        except Service.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Service not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    # In case of GET request, render the page with available services
    services = Service.objects.all()
    return render(request, 'user/contactus.html', {'services': services})


def HealthCare(request):
    instructors = InstructorProfile.objects.select_related('user', 'service').prefetch_related('educations')

    for instructor in instructors:
        education_data = instructor.educations.aggregate(
            min_cost=Min('minicost'),
            max_cost=Max('maxcost')
        )
        instructor.min_cost = education_data['min_cost']
        instructor.max_cost = education_data['max_cost']
    return render(request, 'user/healthcare.html', {'instructors': instructors})

def PersonalTrainer(request):
    return render(request, 'user/personaltrainer.html') 



def Beauty(request):
    return render(request, 'user/beauty.html') 



def UserDash(request):
    return render(request, 'user/user-dash.html') 



def UserAppointments(request):
    return render(request, 'user/user-appointments.html') 



@login_required
def UserProfileSettings(request):
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!', extra_tags='success')
            return redirect('core:UserProfileSettings')
        else:
            # Debugging information
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")  # Log errors to console or wherever you're capturing logs
                    messages.error(request, f"{field.capitalize()}: {error}", extra_tags='danger')
            messages.error(request, 'Please correct the errors below.', extra_tags='danger')
    else:
        form = UserProfileUpdateForm(instance=user)
    
    return render(request, 'user/user-profile-settings.html', {
        'form': form,
        'user': user,
    })


@login_required
def UserChangePassword(request):
    user = request.user
    last_change = PasswordChange.objects.filter(user=user).order_by('-timestamp').first()

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
                return redirect('core:UserChangePassword')

    # Clear session variable if user accesses the page without restriction
    request.session['password_redirected'] = False

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            # Save the timestamp of the password change
            PasswordChange.objects.create(user=user)
            # Update the session with the new password
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!', extra_tags='primary')
            return redirect('core:UserChangePassword')
        else:
            # Debugging information
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")  # Log errors to console or wherever you're capturing logs
                    messages.error(request, f"{field.capitalize()}: {error}", extra_tags='danger')
            messages.error(request, 'Please correct the errors below.', extra_tags='danger')
    else:
        form = PasswordChangeForm(user)

    return render(request, 'user/user-change-password.html', {'form': form})





def UserAppointments(request):
    return render(request, 'user/user-appointments.html') 





