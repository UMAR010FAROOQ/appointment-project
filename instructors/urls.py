from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'instructors'

urlpatterns = [
    path("dash/", views.DashPage, name="DashPage"),
    path("appointment-request/", views.AppointmentRequest, name="AppointmentRequest"),
    path("instructor-appointments/", views.InstructorAppointments, name="InstructorAppointments"),
    path("available-timings/", views.AvailableTimings, name="AvailableTimings"),
    path("instructor-profile-settings/", views.InstructorProfileSettings, name="InstructorProfileSettings"),
    path("instructor-change-password/", views.InstructorChangePassword, name="InstructorChangePassword"),


]