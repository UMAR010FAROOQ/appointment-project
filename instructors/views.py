from django.shortcuts import render

# Create your views here.

def DashPage(request):
    return render(request, 'instructors/DashPage.html') 

