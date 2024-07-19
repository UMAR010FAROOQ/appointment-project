from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'authentication'

urlpatterns = [
    path("login/", views.UserLogin, name="user-login"),
    path("register/", views.UserRegister, name="user-register"),
    path('logout/', views.UserLogout, name='user-logout'),
    path('delete_account/', views.DeleteAccount, name='delete-account'),  

    path("instructor-login/", views.InstructorLogin, name="instructor-login"),
    path("instructor-register/", views.InstructorRegister, name="instructor-register"),
    path('logout/', views.UserLogout, name='instructor-logout'),
    path('delete_account/', views.DeleteAccount, name='instructor-delete-account'),  
    path("instructor-forgot/", views.InstructorForgot, name="instructor-forgot"),

    path('reset_password/', views.UserPasswordReset, name='user-forgot'),
    path('reset_password_sent/', views.PasswordResetDone, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirm, name='password_reset_confirm'),
    path('reset_password_complete/', views.PasswordResetComplete, name='password_reset_complete'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
