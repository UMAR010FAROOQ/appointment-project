from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from instructors.models import AvailableTimeSlot

@receiver([post_save, post_delete], sender=AvailableTimeSlot)
def time_slot_changed(sender, instance, **kwargs):
    print(f"[DEBUG] TimeSlot signal triggered for instructor_id: {instance.instructor_id}")

    # Get the channel layer for sending the message
    channel_layer = get_channel_layer()

    # The group name should match the instructor's WebSocket group name
    group_name = str(instance.instructor_id)
    print(f"[DEBUG] Broadcasting to WebSocket group: {group_name}")
    
    # Fetch the updated slots for the day
    available_time_slots = AvailableTimeSlot.objects.filter(
        instructor_id=instance.instructor_id,
        day_of_week=instance.day_of_week,
        is_available=True
    ).order_by('start_time')

    print(f"[DEBUG] Available time slots after update: {available_time_slots}")
    
    # Convert the slots to a list of dicts for serialization and format time
    slots = [{'start_time': slot.start_time.strftime('%I:%M %p'),
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
