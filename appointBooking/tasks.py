# tasks.py
from celery import shared_task
from django.utils import timezone
from instructors.models import AvailableTimeSlot
from appointBooking.models import Appointment
import time


@shared_task
def update_past_time_slots():
    # Get the current date
    current_date = timezone.now().date()

    # Fetch all time slots where the date has passed but are still unavailable
    past_slots = AvailableTimeSlot.objects.filter(date__lt=current_date, is_available=False)

    # Update them to be available
    for slot in past_slots:
        slot.is_available = True
        slot.save()
        print(f"[DEBUG] TimeSlot {slot} is now available again as the date has passed.")


@shared_task
def cancel_unpaid_appointment(appointment_id):
    try:
        # Fetch the appointment record by ID
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check if it's still pending after 10 minutes
        if appointment.status == 'pending':
            appointment.status = 'cancelled'
            appointment.save()
            print(f"[DEBUG] Appointment {appointment_id} was cancelled due to non-payment.")

            # Optional: Trigger the signal to update the slot availability
            from instructors.models import AvailableTimeSlot
            time_slot = AvailableTimeSlot.objects.get(id=appointment.time_slot_id)
            time_slot.is_available = True
            time_slot.save()
    except Appointment.DoesNotExist:
        print(f"[ERROR] Appointment {appointment_id} does not exist.")