from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact
from core.models import Service
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from core.models import PasswordChange
from django.contrib.auth.forms import PasswordChangeForm
from core.forms import UserProfileUpdateForm
from .decorators import simple_user_required
from authentication.models import InstructorProfile
from instructors.models import InstructorProfileInformation, AvailableTimeSlot, Education
from appointBooking.models import Appointment
from django.db.models import Min, Max
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator



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
        education = instructor.educations.first()
        instructor.service_cost = education.service_cost if education else None
        
    return render(request, 'user/healthcare.html', {'instructors': instructors})

def PersonalTrainer(request):
    return render(request, 'user/personaltrainer.html') 



def Beauty(request):
    return render(request, 'user/beauty.html') 


def UserDash(request):
    # Ensure the user is authenticated
    if request.user.is_authenticated:
        # Filter appointments for the logged-in user
        user_appointments = Appointment.objects.filter(user=request.user, status='confirmed')

        # Current date and time
        current_datetime = now()

        # Count upcoming appointments
        upcoming_appointments_count = user_appointments.filter(
            appointment_date__gt=current_datetime.date()
        ).count()

        # Count completed appointments
        completed_appointments_count = user_appointments.filter(
            appointment_date__lt=current_datetime.date()
        ).count()

        # Pass counts to the template
        context = {
            'upcoming_count': upcoming_appointments_count,
            'completed_count': completed_appointments_count,
        }
    else:
        context = {
            'upcoming_count': 0,
            'completed_count': 0,
        }

    return render(request, 'user/user-dash.html', context)


@login_required
def UserAppointments(request):
    user = request.user

    # Fetch user appointments with related data
    user_appointments = Appointment.objects.select_related(
        'instructor__user', 'time_slot'
    ).filter(user=user)

    # Current date for classification
    current_date = now().date()

    # Separate appointments into categories
    upcoming_appointments = user_appointments.filter(
        appointment_date__gte=current_date, status='confirmed'
    ).order_by('appointment_date')
    completed_appointments = user_appointments.filter(
        appointment_date__lt=current_date, status='confirmed'
    ).order_by('-appointment_date')
    cancelled_appointments = user_appointments.filter(
        status='cancelled'
    ).order_by('-appointment_date')

    # Pagination: 5 appointments per page
    paginator_upcoming = Paginator(upcoming_appointments, 4)
    paginator_completed = Paginator(completed_appointments, 4)
    paginator_cancelled = Paginator(cancelled_appointments, 4)

    # Get current page numbers from the query string
    upcoming_page = request.GET.get('upcoming_page', 1)
    completed_page = request.GET.get('completed_page', 1)
    cancelled_page = request.GET.get('cancelled_page', 1)

    # Paginate results
    upcoming_paginated = paginator_upcoming.get_page(upcoming_page)
    completed_paginated = paginator_completed.get_page(completed_page)
    cancelled_paginated = paginator_cancelled.get_page(cancelled_page)

    # Determine active tab
    active_tab = 'pills-upcoming'  # Default to upcoming tab
    if 'completed_page' in request.GET:
        active_tab = 'pills-complete'
    elif 'cancelled_page' in request.GET:
        active_tab = 'pills-cancelled'

    # Prepare context for the template
    context = {
        'upcoming_appointments': upcoming_paginated,
        'completed_appointments': completed_paginated,
        'cancelled_appointments': cancelled_paginated,
        'active_tab': active_tab,
    }

    return render(request, 'user/user-appointments.html', context)


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


def InstructorProfileDetail(request, pk):
    instructor = get_object_or_404(InstructorProfile, pk=pk)
    profile_info = instructor.profile_info.all()
    available_times = instructor.available_times.all().order_by('day_of_week', 'start_time')  # Retrieve and order time slots

    # Group time slots by day
    days_of_week = {
        'Monday': available_times.filter(day_of_week='Monday'),
        'Tuesday': available_times.filter(day_of_week='Tuesday'),
        'Wednesday': available_times.filter(day_of_week='Wednesday'),
        'Thursday': available_times.filter(day_of_week='Thursday'),
        'Friday': available_times.filter(day_of_week='Friday'),
        'Saturday': available_times.filter(day_of_week='Saturday'),
        'Sunday': available_times.filter(day_of_week='Sunday')
    }

    return render(request, 'user/instructor-profile.html', {
        'instructor': instructor,
        'profile_info': profile_info,
        'days_of_week': days_of_week,  # Pass the grouped time slots to the template
    })
