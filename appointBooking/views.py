# views.py
from django.shortcuts import render, get_object_or_404
from authentication.models import InstructorProfile
from instructors.models import AvailableTimeSlot
from django.http import JsonResponse
from datetime import datetime



def AppointBooking(request, pk):
    instructor = get_object_or_404(InstructorProfile, pk=pk)
    available_time_slots = AvailableTimeSlot.objects.filter(instructor=instructor, is_available=True).order_by('start_time')

    return render(request, 'appointbooking/appointment.html', {
        'instructor': instructor,
        'available_time_slots': available_time_slots,
    })


def fetch_time_slots(request):
    instructor_id = request.GET.get('instructor_id')
    selected_date = request.GET.get('selected_date')

    if not instructor_id or not selected_date:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    try:
        date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
        weekday = date_obj.strftime('%A')  # Get full name of the day (e.g., 'Monday')

        available_time_slots = AvailableTimeSlot.objects.filter(
            instructor_id=instructor_id,
            day_of_week=weekday,
            is_available=True
        ).order_by('start_time')

        slots = [{'start_time': slot.start_time.strftime('%H:%M'), 'end_time': slot.end_time.strftime('%H:%M')}
                 for slot in available_time_slots]

        return JsonResponse(slots, safe=False)

    except Exception as e:
        print(f"Error: {str(e)}")  # Log error to the console
        return JsonResponse({'error': str(e)}, status=500)