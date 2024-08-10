from django.db import models
from django.utils import timezone
from django.conf import settings

class Service(models.Model):
    name = models.CharField(max_length=100)
    heading = models.CharField(max_length=200)
    content = models.TextField(max_length=800)
    image = models.ImageField(upload_to='service_images/')

    def __str__(self):
        return self.name
    

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    service = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    message = models.TextField()

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
    


class PasswordChange(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.email} - {self.timestamp}'