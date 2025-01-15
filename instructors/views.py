from django.shortcuts import render
from .decorators import instructor_required
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from instructors.models import InstructorPasswordChange, Education, InstructorProfileInformation, AvailableTimeSlot
from django.contrib.auth.forms import PasswordChangeForm
from authentication.models import InstructorProfile, CustomUser
from .forms import InstructorProfileUpdateForm, CustomUserUpdateForm, EducationForm, AvailableTimeSlotForm
from core.models import Service
from django.db.models import Q
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import traceback



@instructor_required
def DashPage(request):
    return render(request, 'instructors/index.html') 


def AppointmentRequest(request):
    return render(request, 'instructors/appointment-request.html') 



def InstructorAppointments(request):
    return render(request, 'instructors/instructor-appointments.html') 




@login_required
def available_timings(request):
    # Fetch the instructor profile related to the logged-in user
    instructor_profile = get_object_or_404(InstructorProfile, user=request.user)

    # Initialize the form and fetch available slots for this instructor profile
    form = AvailableTimeSlotForm()
    available_slots = AvailableTimeSlot.objects.filter(instructor=instructor_profile)

    # Pass all necessary context variables
    context = {
        'form': form,
        'available_slots': available_slots,
        'instructor': instructor_profile,
    }

    return render(request, 'instructors/available-timings.html', context)



@csrf_exempt
@login_required
def manage_time_slot(request):
    instructor_profile = get_object_or_404(InstructorProfile, user=request.user)

    if request.method == 'POST':
        # Extract data manually from POST request
        form = AvailableTimeSlotForm(request.POST)

        if form.is_valid():
            # Create the time slot but don't save to DB yet
            time_slot = form.save(commit=False)
            time_slot.instructor = instructor_profile  # Associate the time slot with the instructor
            time_slot.save()  # Now save it to the DB
            return JsonResponse({'status': 'success', 'message': 'Time slot saved successfully.'})
        else:
            # Return form errors as JSON response
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': 'Invalid form data.', 'errors': errors}, status=400)

    elif request.method == 'DELETE':
        slot_id = request.GET.get('slot_id')
        day = request.GET.get('day')

        try:
            if slot_id:
                time_slot = get_object_or_404(AvailableTimeSlot, id=slot_id, instructor=instructor_profile)
                time_slot.delete()
                return JsonResponse({'status': 'success', 'message': 'Time slot deleted successfully.'})
            elif day:
                # Delete all slots for the specified day
                AvailableTimeSlot.objects.filter(instructor=instructor_profile, day_of_week=day).delete()
                return JsonResponse({'status': 'success', 'message': f'All time slots for {day} deleted successfully.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Slot ID or Day is required.'}, status=400)

        except Exception as e:
            print(f"Error deleting time slot: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while deleting the time slot(s).'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)




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
            'speciality': education.speciality,
            'service_cost': education.service_cost,
            'aboutme': education.aboutme,
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

        elif 'speciality' in request.POST:  # Education form submission
            education_form = EducationForm(request.POST, instance=education)
            if education_form.is_valid():
                education = education_form.save(commit=False)
                education.instructor = instructor
                education.save()
                messages.success(request, 'Your information details have been updated successfully!', extra_tags='success')
            else:
                for field, errors in education_form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"{field.capitalize()}: {error}", extra_tags='danger')
                messages.error(request, 'Please correct the errors in your information details.', extra_tags='danger')

    return render(request, 'instructors/instructor-profile-settings.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'education_form': education_form,
        'user': user,
        'services': Service.objects.all(),
    })






# Helper function to handle errors for all forms
def handle_form_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            print(f"Error in {field}: {error}")
            messages.error(form.request, f"{field.capitalize()}: {error}", extra_tags='danger')
    messages.error(form.request, 'Please correct the errors in your information details.', extra_tags='danger')



def InstructorProfileInfo(request):
    instructor = get_object_or_404(InstructorProfile, user=request.user)

    if request.method == 'POST':
        if 'personal-info-submit' in request.POST:
            # Check for existing record based on unique fields
            institution_name = request.POST.get('institution_name')
            course = request.POST.get('course')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            marks = request.POST.get('marks')

            # Create a new record; do not update existing ones
            try:
                existing_education = InstructorProfileInformation.objects.filter(
                    instructor=instructor,
                    institution_name=institution_name,
                    course=course,
                    start_date=start_date,
                    end_date=end_date
                )
                if existing_education.exists():
                    messages.warning(request, 'Similar education information already exists.')
                else:
                    InstructorProfileInformation.objects.create(
                        instructor=instructor,
                        institution_name=institution_name,
                        course=course,
                        start_date=start_date,
                        end_date=end_date,
                        marks=marks
                    )
                    messages.success(request, 'Education information saved successfully.')
            except Exception as e:
                messages.error(request, f'Error saving education information: {str(e)}')

        elif 'work-history-submit' in request.POST:
            work_history_institution = request.POST.get('work_history_institution')
            work_start_date = request.POST.get('work_start_date')
            work_end_date = request.POST.get('work_end_date')

            try:
                existing_work_history = InstructorProfileInformation.objects.filter(
                    instructor=instructor,
                    work_history_institution=work_history_institution,
                    work_start_date=work_start_date,
                    work_end_date=work_end_date
                )
                if existing_work_history.exists():
                    messages.warning(request, 'Similar work history information already exists.')
                else:
                    InstructorProfileInformation.objects.create(
                        instructor=instructor,
                        work_history_institution=work_history_institution,
                        work_start_date=work_start_date,
                        work_end_date=work_end_date
                    )
                    messages.success(request, 'Work history information saved successfully.')
            except Exception as e:
                messages.error(request, f'Error saving work history information: {str(e)}')

        elif 'instructor-services-submit' in request.POST:
            services = request.POST.get('instructor_services')

            try:
                existing_services = InstructorProfileInformation.objects.filter(
                    instructor=instructor,
                    services=services
                )
                if existing_services.exists():
                    messages.warning(request, 'Similar services information already exists.')
                else:
                    InstructorProfileInformation.objects.create(
                        instructor=instructor,
                        services=services
                    )
                    messages.success(request, 'Services information saved successfully.')
            except Exception as e:
                messages.error(request, f'Error saving services information: {str(e)}')

        elif 'instructor-specializations-submit' in request.POST:
            specializations = request.POST.get('instructor_specializations')

            try:
                existing_specializations = InstructorProfileInformation.objects.filter(
                    instructor=instructor,
                    specializations=specializations
                )
                if existing_specializations.exists():
                    messages.warning(request, 'Similar specializations information already exists.')
                else:
                    InstructorProfileInformation.objects.create(
                        instructor=instructor,
                        specializations=specializations
                    )
                    messages.success(request, 'Specializations information saved successfully.')
            except Exception as e:
                messages.error(request, f'Error saving specializations information: {str(e)}')

        elif 'workspace-img-submit' in request.POST and request.FILES:
            workspace_image = request.FILES.get('workspace_image')

            try:
                existing_image = InstructorProfileInformation.objects.filter(
                    instructor=instructor,
                    workspace_image=workspace_image
                )
                if existing_image.exists():
                    messages.warning(request, 'Similar workspace image already exists.')
                else:
                    InstructorProfileInformation.objects.create(
                        instructor=instructor,
                        workspace_image=workspace_image
                    )
                    messages.success(request, 'Workspace image saved successfully.')
            except Exception as e:
                messages.error(request, f'Error saving workspace image: {str(e)}')

        return redirect('instructors:InstructorProfileInfo')

    context = {
        'instructor': instructor,
    }

    return render(request, 'instructors/instructor-profile-info.html', context)





def manage_profile(request):
    # Fetch the currently logged-in instructor's profile
    instructor_profile = get_object_or_404(InstructorProfile, user=request.user)

    # Retrieve all associated information records for the instructor
    instructor_profile_info = InstructorProfileInformation.objects.filter(instructor=instructor_profile)

    if request.method == 'POST':
        # Handle update and delete operations
        action = request.POST.get('action')
        entry_id = request.POST.get('entry_id')

        if action and entry_id:
            entry = get_object_or_404(InstructorProfileInformation, id=entry_id)

            if action == 'delete':
                entry.delete()
                messages.success(request, 'Profile entry deleted successfully.')
                return redirect('instructors:manage_profile')

            elif action == 'update':
                # Handle empty or incorrect date fields
                start_date = request.POST.get('start_date', entry.start_date)
                end_date = request.POST.get('end_date', entry.end_date)
                work_start_date = request.POST.get('work_start_date', entry.work_start_date)
                work_end_date = request.POST.get('work_end_date', entry.work_end_date)

                # Update the entry fields
                entry.institution_name = request.POST.get('institution_name', entry.institution_name)
                entry.course = request.POST.get('course', entry.course)
                entry.start_date = start_date if start_date else None
                entry.end_date = end_date if end_date else None
                entry.work_history_institution = request.POST.get('work_history_institution', entry.work_history_institution)
                entry.work_start_date = work_start_date if work_start_date else None
                entry.work_end_date = work_end_date if work_end_date else None
                entry.services = request.POST.get('services', entry.services)
                entry.specializations = request.POST.get('specializations', entry.specializations)

                if 'workspace_image' in request.FILES:
                    entry.workspace_image = request.FILES['workspace_image']

                try:
                    entry.save()
                    messages.success(request, 'Profile entry updated successfully.')
                except ValidationError as e:
                    messages.error(request, f"Error updating profile: {e}")

                return redirect('instructors:manage_profile')

    context = {
        'instructor_profile': instructor_profile,
        'instructor_profile_info': instructor_profile_info,
    }

    return render(request, 'instructors/profile-info-manage.html', context)





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





