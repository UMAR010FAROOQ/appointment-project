from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from instructors.models import AvailableTimeSlot
from appointBooking.models import Appointment
from django.utils import timezone

@receiver([post_save, post_delete], sender=AvailableTimeSlot)
def time_slot_changed(sender, instance, **kwargs):
    print(f"[DEBUG] TimeSlot signal triggered for instructor_id: {instance.instructor_id}")

    # Get the channel layer for sending the message
    channel_layer = get_channel_layer()

    # The group name should match the instructor's WebSocket group name
    group_name = str(instance.instructor_id)
    print(f"[DEBUG] Broadcasting to WebSocket group: {group_name}")

    # Mark time slot as unavailable if it's booked
    if instance.is_available == False:
        print(f"[DEBUG] TimeSlot {instance} is booked and now unavailable.")

    # Fetch the updated slots for the day (only future dates)
    current_date = timezone.now().date()
    available_time_slots = AvailableTimeSlot.objects.filter(
        instructor_id=instance.instructor_id,
        day_of_week=instance.day_of_week,
        is_available=True,
        date__gte=current_date  # Ensure only future slots are fetched
    ).order_by('start_time')

    print(f"[DEBUG] Available time slots after update: {available_time_slots}")

    # Convert the slots to a list of dicts for serialization and format time
    slots = [{'id': slot.id,
              'start_time': slot.start_time.strftime('%I:%M %p'),
              'end_time': slot.end_time.strftime('%I:%M %p')} 
             for slot in available_time_slots]

    # Send the message to the WebSocket group
    async_to_sync(channel_layer.group_send)(
        group_name, 
        {
            'type': 'time_slot_update',  # This is the handler that will be called in the consumer
            'slots': slots
        }
    )


@receiver(post_save, sender=Appointment)
def handle_appointment_cancellation(sender, instance, **kwargs):
    if instance.status == 'cancelled':
        # Mark the associated slot as available
        time_slot = AvailableTimeSlot.objects.get(id=instance.time_slot_id)
        time_slot.is_available = True
        time_slot.save()

        print(f"[DEBUG] Appointment cancelled, time slot {time_slot} is now available.")

        # Trigger the time slot update signal
        time_slot_changed(sender=AvailableTimeSlot, instance=time_slot)


@receiver(post_save, sender=Appointment)
def handle_appointment_creation(sender, instance, **kwargs):
    if instance.status == 'confirmed':
        # Mark the associated slot as unavailable
        time_slot = AvailableTimeSlot.objects.get(id=instance.time_slot_id)
        time_slot.is_available = False
        time_slot.save()

        print(f"[DEBUG] Appointment confirmed, time slot {time_slot} is now unavailable.")
