from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'appointBooking'

urlpatterns = [
    path('booking/<int:pk>/', views.AppointBooking, name='AppointBooking'),
    path('fetch-slots/', views.fetch_time_slots, name='fetch_time_slots'), 


]