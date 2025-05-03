from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from instructors.models import AvailableTimeSlot
from appointBooking.models import Appointment
from django.utils import timezone
from appointBooking.tasks import cancel_unpaid_appointment


@receiver([post_save, post_delete], sender=AvailableTimeSlot)
def time_slot_changed(sender, instance, **kwargs):
    print(f"[DEBUG] TimeSlot signal triggered for instructor_id: {instance.instructor_id}")

    channel_layer = get_channel_layer()
    group_name = str(instance.instructor_id)
    print(f"[DEBUG] Broadcasting to WebSocket group: {group_name}")

    # Fetch updated slots only for future dates
    current_date = timezone.now().date()
    available_time_slots = AvailableTimeSlot.objects.filter(
        instructor_id=instance.instructor_id,
        day_of_week=instance.day_of_week,
        is_available=True,
        date__gte=current_date
    ).order_by('start_time')

    print(f"[DEBUG] Available time slots after update: {available_time_slots}")

    # Prepare slots for serialization
    slots = [{'id': slot.id,
              'start_time': slot.start_time.strftime('%I:%M %p'),
              'end_time': slot.end_time.strftime('%I:%M %p')} 
             for slot in available_time_slots]

    # Send the message to the WebSocket group
    async_to_sync(channel_layer.group_send)(
        group_name, 
        {
            'type': 'time_slot_update',
            'slots': slots
        }
    )

@receiver(post_save, sender=Appointment)
def handle_appointment_creation(sender, instance, **kwargs):
    if instance.status == 'confirmed':
        time_slot = AvailableTimeSlot.objects.get(id=instance.time_slot_id)
        time_slot.is_available = False
        time_slot.save()
        print(f"[DEBUG] Appointment confirmed, time slot {time_slot} is now unavailable.")

@receiver(post_save, sender=Appointment)
def handle_appointment_cancellation(sender, instance, **kwargs):
    if instance.status == 'cancelled':
        time_slot = AvailableTimeSlot.objects.get(id=instance.time_slot_id)
        time_slot.is_available = True
        time_slot.save()
        print(f"[DEBUG] Appointment cancelled, time slot {time_slot} is now available.")
        time_slot_changed(sender=AvailableTimeSlot, instance=time_slot)


# NEW SIGNAL FOR APPOINTMENT DELETION
@receiver(post_delete, sender=Appointment)
def handle_appointment_deletion(sender, instance, **kwargs):
    """
    Ensure the time slot becomes available again if an appointment is deleted.
    """
    try:
        time_slot = AvailableTimeSlot.objects.get(id=instance.time_slot_id)
        time_slot.is_available = True
        time_slot.save()
        print(f"[DEBUG] Appointment deleted, time slot {time_slot} is now available.")
        time_slot_changed(sender=AvailableTimeSlot, instance=time_slot)
    except AvailableTimeSlot.DoesNotExist:
        print("[ERROR] Time slot for deleted appointment does not exist.")



@receiver(post_save, sender=Appointment)
def start_cancellation_task(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        # Schedule cancellation task for 10 minutes after creation
        cancel_unpaid_appointment.apply_async((instance.id,), countdown=600)
        print(f"[DEBUG] Cancellation task scheduled for Appointment {instance.id} in 10 minutes.")
    
    if instance.status == 'confirmed':
        # If the appointment is confirmed, make the slot unavailable
        time_slot = AvailableTimeSlot.objects.get(id=instance.time_slot_id)
        time_slot.is_available = False
        time_slot.save()
        print(f"[DEBUG] Appointment confirmed, time slot {time_slot} is now unavailable.")

@receiver(post_save, sender=Appointment)
def handle_appointment_cancellation(sender, instance, **kwargs):
    if instance.status == 'cancelled':
        time_slot = AvailableTimeSlot.objects.get(id=instance.time_slot_id)
        time_slot.is_available = True
        time_slot.save()
        print(f"[DEBUG] Appointment cancelled, time slot {time_slot} is now available.")

@receiver(post_delete, sender=Appointment)
def handle_appointment_deletion(sender, instance, **kwargs):
    try:
        time_slot = AvailableTimeSlot.objects.get(id=instance.time_slot_id)
        time_slot.is_available = True
        time_slot.save()
        print(f"[DEBUG] Appointment deleted, time slot {time_slot} is now available.")
    except AvailableTimeSlot.DoesNotExist:
        print("[ERROR] Time slot for deleted appointment does not exist.")