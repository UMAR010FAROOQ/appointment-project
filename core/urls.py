from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'core'

urlpatterns = [
    path("", views.HomePage, name="HomePage"),
    path("aboutus/", views.AboutPage, name="AboutPage"),
    path("contactus/", views.ContactPage, name="ContactPage"),
    path("healthcare/", views.HealthCare, name="HealthCare"),
    path("personaltrainer/", views.PersonalTrainer, name="PersonalTrainer"),
    path("beauty/", views.Beauty, name="Beauty"),

    path("user-dash/", views.UserDash, name="UserDash"),
    path("user-appointments/", views.UserAppointments, name="UserAppointments"),
    path("user-profile-settings/", views.UserProfileSettings, name="UserProfileSettings"),
    path("user-change-password/", views.UserChangePassword, name="UserChangePassword"),


]