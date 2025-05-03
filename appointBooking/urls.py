from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'appointBooking'

urlpatterns = [
    path('booking/<int:pk>/', views.AppointBooking, name='appointment_booking'),
    # path('fetch-slots/', views.fetch_time_slots, name='fetch_time_slots'), 
    path('checkout/<int:appointment_id>/', views.AppointCheckout, name='appointment_checkout'),
    path('success/', views.AppointSuccess, name='appointment_success'),
    path('cancelled/', views.AppointCancelled, name='appointment_cancelled'),
    path('add-to-google-calendar/', views.add_to_google_calendar, name='add_to_google_calendar'),

]