# models.py
from django.db import models
from django.utils import timezone
from django.conf import settings
from authentication.models import InstructorProfile


class InstructorPasswordChange(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.email} - {self.timestamp}'


class Education(models.Model):
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='educations')
    institution_name = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    marks = models.CharField(max_length=100)
    description = models.TextField()
    speciality = models.CharField(max_length=255, default="")
    minicost = models.IntegerField(blank=True, null=True)
    maxcost = models.IntegerField(blank=True, null=True)


    def __str__(self):
        return f"{self.course} at {self.institution_name}"
