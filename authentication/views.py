from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import CustomUser, InstructorProfile, CustomUser, SimpleUserProfile
from instructors.models import Service
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, get_backends, authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.conf import settings
import requests
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .forms import CustomSetPasswordForm


User = get_user_model()


def UserLogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # Check if "Remember Me" checkbox is checked
        recaptcha_response = request.POST.get('g-recaptcha-response')

        # Verify reCAPTCHA response
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        params = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response,
        }
        response = requests.post(verify_url, data=params)
        result = response.json()

        if result['success']:
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.is_active:
                    # Set session expiration
                    if remember_me:
                        request.session.set_expiry(settings.SESSION_COOKIE_AGE_REMEMBER)  # 10 days
                    else:
                        request.session.set_expiry(settings.SESSION_COOKIE_AGE)  # Default: 1 hour

                    login(request, user)
                    messages.success(request, "Login successful.", extra_tags='primary')
                    return redirect('core:HomePage')
                else:
                    messages.error(request, "Your account is inactive. Please contact support.", extra_tags='danger')
            else:
                messages.error(request, "Invalid email or password.", extra_tags='danger')
        else:
            messages.error(request, "reCAPTCHA verification failed. Please try again.", extra_tags='danger')

    return render(request, 'authentication/user-login.html', {'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY})


def UserRegister(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        profile_image = request.FILES.get('userProfileImg')

        if password1 != password2:
            messages.error(request, "Passwords do not match.", extra_tags='danger')
            return redirect('authentication:user-register')

        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            if SimpleUserProfile.objects.filter(user=user).exists():
                messages.error(request, "Email already registered as a simple user.", extra_tags='danger')
                return redirect('authentication:user-register')
        else:
            user = CustomUser(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=make_password(password1),
                profile_image=profile_image,
                is_active=True,  # Default to active for users
            )
            user.save()

        SimpleUserProfile.objects.create(user=user)

        backend = get_backends()[0]
        user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

        login(request, user)
        messages.success(request, "Registration successful.", extra_tags='primary')
        return redirect('authentication:user-login')

    return render(request, 'authentication/user-register.html')


def UserLogout(request):
    logout(request)
    messages.success(request, "Logout successful", extra_tags='primary')
    return redirect('authentication:user-login')


@login_required
def DeleteAccount(request):
    user = request.user
    user.delete()
    messages.success(request, "Your account has been deleted successfully.")
    return redirect('authentication:user-login')



def InstructorLogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # Check if "Remember Me" checkbox is checked
        recaptcha_response = request.POST.get('g-recaptcha-response')

        # Verify reCAPTCHA response
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        params = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response,
        }
        response = requests.post(verify_url, data=params)
        result = response.json()

        if result['success']:
            user = authenticate(request, email=email, password=password)

            if user is not None and InstructorProfile.objects.filter(user=user).exists():
                if user.is_active and hasattr(user, 'instructorprofile')  and user.instructorprofile.is_active:
                    # Set session expiration
                    if remember_me:
                        request.session.set_expiry(settings.SESSION_COOKIE_AGE_REMEMBER)  # 10 days
                    else:
                        request.session.set_expiry(settings.SESSION_COOKIE_AGE)  # Default: 1 hour

                    login(request, user)
                    messages.success(request, "Login successful.", extra_tags='primary')
                    return redirect('instructors:DashPage')
                else:
                    messages.error(request, "Your account is inactive or not an instructor. Please contact support.", extra_tags='danger')
            else:
                messages.error(request, "Invalid email or password.", extra_tags='danger')
        else:
            messages.error(request, "reCAPTCHA verification failed. Please try again.", extra_tags='danger')

    return render(request, 'authentication/instructor-login.html', {'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY})


def InstructorRegister(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        city = request.POST.get('city')
        service_id = request.POST.get('service')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        profile_image = request.FILES.get('userProfileImg')

        if password1 != password2:
            messages.error(request, "Passwords do not match.", extra_tags='danger')
            return redirect('authentication:instructor-register')

        service = Service.objects.get(id=service_id)

        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            if InstructorProfile.objects.filter(user=user).exists():
                messages.error(request, "Email already registered as an instructor.", extra_tags='danger')
                return redirect('authentication:instructor-register')
        else:
            user = CustomUser(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=make_password(password1),
                profile_image=profile_image,
                is_active=False,  # Default to inactive until approved by super admin
            )
            user.save()

        InstructorProfile.objects.create(
            user=user,
            city=city,
            service=service,
        )

        backend = get_backends()[0]
        user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

        login(request, user)
        messages.success(request, "Registration successful. Please wait for approval.", extra_tags='primary')
        return redirect('authentication:instructor-login')

    services = Service.objects.all()
    return render(request, 'authentication/instructor-register.html', {'services': services})



def InstructorLogout(request):
    logout(request)
    messages.success(request, "Logout successful", extra_tags='primary')
    return redirect('authentication:instructor-login')


@login_required
def InstructorDeleteAccount(request):
    user = request.user
    user.delete()
    messages.success(request, "Your account has been deleted successfully.")
    return redirect('authentication:instructor-login')




def InstructorForgot(request):
    return render(request, 'authentication/instructor-forgot.html') 



# User forgot password
def UserPasswordReset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            subject = 'Password Reset Requested'
            email_template_name = 'authentication/password_reset_email.html'
            context = {
                "email": email,
                'domain': request.META['HTTP_HOST'],
                'site_name': 'appointment',
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
            }
            email_content = render_to_string(email_template_name, context)
            send_mail(subject, email_content, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
            messages.success(request, 'A password reset link has been sent to your email.', extra_tags='primary')
            return redirect('authentication:password_reset_done')
        else:
            messages.error(request, 'Invalid email address.', extra_tags='danger')

    return render(request, 'authentication/password_reset_form.html')

def PasswordResetDone(request):
    return render(request, 'authentication/password_reset_done.html')

def PasswordResetConfirm(request, uidb64=None, token=None):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Password has been reset.', extra_tags='primary')
                return redirect('authentication:password_reset_complete')
            else:
                messages.error(request, 'Please correct the errors below.', extra_tags='danger')
        else:
            form = CustomSetPasswordForm(user)
        return render(request, 'authentication/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The reset link is no longer valid.', extra_tags='danger')
        return redirect('authentication:password_reset_done')

def PasswordResetComplete(request):
    return render(request, 'authentication/password_reset_complete.html')