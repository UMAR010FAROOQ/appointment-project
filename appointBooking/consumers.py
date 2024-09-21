import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from channels.db import database_sync_to_async  # Import database_sync_to_async

class TimeSlotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.instructor_id = self.scope['url_route']['kwargs']['instructor_id']
        
        # Add to instructor group
        await self.channel_layer.group_add(self.instructor_id, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Discard from group
        await self.channel_layer.group_discard(self.instructor_id, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        selected_date = data.get('selected_date')

        try:
            # Convert selected date string to a date object
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
            weekday = date_obj.strftime('%A')

            # Fetch the available time slots asynchronously
            available_time_slots = await self.get_available_time_slots(weekday)

            # Create a list of time slots to send back, converting time to string
            slots = [{'start_time': slot['start_time'].strftime('%H:%M'), 
                      'end_time': slot['end_time'].strftime('%H:%M')}
                     for slot in available_time_slots]

            await self.send(text_data=json.dumps(slots))

        except Exception as e:
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

        # Convert the QuerySet to a list of dicts for easier JSON serialization
        return list(available_time_slots.values('start_time', 'end_time'))
