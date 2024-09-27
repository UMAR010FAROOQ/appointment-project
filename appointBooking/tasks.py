# tasks.py
from celery import shared_task
from django.utils import timezone
from instructors.models import AvailableTimeSlot

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
