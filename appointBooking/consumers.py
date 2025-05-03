import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from channels.db import database_sync_to_async

class TimeSlotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.instructor_id = self.scope['url_route']['kwargs']['instructor_id']
        print(f"[DEBUG] WebSocket connection established for instructor_id: {self.instructor_id}")

        # Add to instructor group
        await self.channel_layer.group_add(self.instructor_id, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print(f"[DEBUG] WebSocket disconnected for instructor_id: {self.instructor_id}, close_code: {close_code}")
        # Discard from group
        await self.channel_layer.group_discard(self.instructor_id, self.channel_name)

    async def receive(self, text_data):
        print(f"[DEBUG] WebSocket received data: {text_data}")
        data = json.loads(text_data)
        selected_date = data.get('selected_date')
        
        try:
            # Convert selected date string to a date object
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
            weekday = date_obj.strftime('%A')
            print(f"[DEBUG] Selected date: {selected_date}, Weekday: {weekday}")

            # Fetch the available time slots asynchronously
            available_time_slots = await self.get_available_time_slots(weekday)
            print(f"[DEBUG] Available time slots: {available_time_slots}")

            # Create a list of time slots to send back, converting time to 12-hour format with AM/PM
            slots = [{'id': slot['id'],'start_time': slot['start_time'].strftime('%I:%M %p'), 
                      'end_time': slot['end_time'].strftime('%I:%M %p')}
                     for slot in available_time_slots]

            await self.send(text_data=json.dumps(slots))

        except Exception as e:
            print(f"[DEBUG] Error in WebSocket: {e}")
            await self.send(text_data=json.dumps({'error': str(e)}))

    @database_sync_to_async
    def get_available_time_slots(self, weekday):
        from instructors.models import AvailableTimeSlot
        
        # Fetch time slots from the database (this is synchronous, but now wrapped in database_sync_to_async)
        available_time_slots = AvailableTimeSlot.objects.filter(
            instructor_id=self.instructor_id,
            day_of_week=weekday,
            is_available=True
        ).order_by('start_time')

        print(f"[DEBUG] Querying available time slots for weekday: {weekday}")
        
        # Convert the QuerySet to a list of dicts for easier JSON serialization
        return list(available_time_slots.values('id','start_time', 'end_time'))

    # Method to handle the time slot update
    async def time_slot_update(self, event):
        print(f"[DEBUG] Time slot update triggered: {event}")
        slots = event['slots']
        # Log to confirm the slots contain 'id'
        print(f"[DEBUG] Slots with ID being sent: {slots}")
        # Send the updated slots to the connected client
        await self.send(text_data=json.dumps(slots))
