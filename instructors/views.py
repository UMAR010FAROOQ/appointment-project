from django.shortcuts import render
from .decorators import instructor_required


@instructor_required
def DashPage(request):
    return render(request, 'instructors/index.html') 


def AppointmentRequest(request):
    return render(request, 'instructors/appointment-request.html') 



def InstructorAppointments(request):
    return render(request, 'instructors/instructor-appointments.html') 



def AvailableTimings(request):
    return render(request, 'instructors/available-timings.html') 




def InstructorProfileSettings(request):
    return render(request, 'instructors/instructor-profile-settings.html') 



def InstructorChangePassword(request):
    return render(request, 'instructors/instructor-change-password.html') 

