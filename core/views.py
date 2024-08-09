from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact
from core.models import Service
from django.http import JsonResponse

# Create your views here.

def HomePage(request):
    services = Service.objects.all()
    return render(request, 'user/index.html', {'services': services})



def AboutPage(request):
    return render(request, 'user/aboutus.html') 


def ContactPage(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get('name')
        email = request.POST.get('email')
        country = request.POST.get('country')
        city = request.POST.get('city')
        service_id = request.POST.get('service')
        gender = request.POST.get('gender')
        message = request.POST.get('message')

        # Validate that all fields are present
        if not all([name, email, country, city, service_id, gender, message]):
            return JsonResponse({'success': False, 'error': 'All fields are required.'})

        # Save the data to the database
        try:
            service = Service.objects.get(id=service_id)
            contact = Contact.objects.create(
                name=name,
                email=email,
                country=country,
                city=city,
                service=service,
                gender=gender,
                message=message
            )
            contact.save()
            return JsonResponse({'success': True})
        except Service.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Service not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    # In case of GET request, render the page with available services
    services = Service.objects.all()
    return render(request, 'user/contactus.html', {'services': services})



def HealthCare(request):
    return render(request, 'user/healthcare.html') 



def PersonalTrainer(request):
    return render(request, 'user/personaltrainer.html') 



def Beauty(request):
    return render(request, 'user/beauty.html') 



def UserDash(request):
    return render(request, 'user/user-dash.html') 



def UserAppointments(request):
    return render(request, 'user/user-appointments.html') 



def UserProfileSettings(request):
    return render(request, 'user/user-profile-settings.html') 




def UserChangePassword(request):
    return render(request, 'user/user-change-password.html') 

