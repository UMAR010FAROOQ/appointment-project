# views.py
from django.shortcuts import render, get_object_or_404
from authentication.models import InstructorProfile
from instructors.models import AvailableTimeSlot
from appointBooking.models import Appointment
from django.http import JsonResponse
from datetime import datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def AppointBooking(request, pk):
    instructor = get_object_or_404(InstructorProfile, pk=pk)
    available_time_slots = AvailableTimeSlot.objects.filter(instructor=instructor, is_available=True).order_by('start_time')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        appointment_date = request.POST.get('appointment_date')
        time_slot_id = request.POST.get('time_slot')
        
        if not appointment_date or not time_slot_id:
            return JsonResponse({"success": False, "error": "Select a time slot."})


        # Print data to the terminal for debugging
        print(f"Received POST data: \n"
              f"First Name: {first_name}, Last Name: {last_name}, Email: {email}, Phone: {phone}, Address: {address}, "
              f"Appointment Date: {appointment_date}, Time Slot ID: {time_slot_id}")

        # Validate fields
        if not all([first_name, last_name, email, phone, address, appointment_date, time_slot_id]):
            return JsonResponse({'success': False, 'error': 'All fields are required, including selecting a time slot.'})


        if not time_slot_id:
            return JsonResponse({'error': 'Please select a time slot.'}, status=400)

        # Fetch the selected time slot
        try:
            time_slot = AvailableTimeSlot.objects.get(pk=time_slot_id)
            print(f"Selected Time Slot: Start Time - {time_slot.start_time}, End Time - {time_slot.end_time}, Available - {time_slot.is_available}")
        except AvailableTimeSlot.DoesNotExist:
            print(f"Time Slot with ID {time_slot_id} does not exist.")
            return JsonResponse({'error': 'Selected time slot does not exist.'}, status=404)

        # Create and save the appointment
        appointment = Appointment.objects.create(
            instructor=instructor,
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            appointment_date=appointment_date,
            time_slot=time_slot_id,
            status='pending'
        )

        # Mark the selected time slot as unavailable
        time_slot.is_available = False
        time_slot.save()

        print(f"Appointment created successfully for {first_name} {last_name} on {appointment_date}.")

        return JsonResponse({'message': 'Appointment booked successfully!'})

    return render(request, 'appointbooking/appointment.html', {
        'instructor': instructor,
        'available_time_slots': available_time_slots,
    })



# def fetch_time_slots(request):
#     instructor_id = request.GET.get('instructor_id')
#     selected_date = request.GET.get('selected_date')

#     if not instructor_id or not selected_date:
#         return JsonResponse({'error': 'Invalid parameters'}, status=400)

#     try:
#         date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
#         weekday = date_obj.strftime('%A')  

#         available_time_slots = AvailableTimeSlot.objects.filter(
#             instructor_id=instructor_id,
#             day_of_week=weekday,
#             is_available=True
#         ).order_by('start_time')

#         slots = [{'start_time': slot.start_time.strftime('%H:%M'), 'end_time': slot.end_time.strftime('%H:%M')}
#                  for slot in available_time_slots]

#         return JsonResponse(slots, safe=False)

#     except Exception as e:
#         print(f"Error: {str(e)}") 
#         return JsonResponse({'error': str(e)}, status=500)