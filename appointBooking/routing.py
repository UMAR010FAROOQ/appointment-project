from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/appointbooking/fetch-slots/(?P<instructor_id>\d+)/$', consumers.TimeSlotConsumer.as_asgi()),
]
