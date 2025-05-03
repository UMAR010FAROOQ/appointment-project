# models.py
from django.db import models
from django.utils import timezone
from django.conf import settings
from authentication.models import InstructorProfile
from django.core.exceptions import ValidationError
from datetime import date

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
    service_cost = models.IntegerField(blank=True, null=True)
    aboutme = models.CharField(max_length=650, default="")

    def __str__(self):
        return f"{self.course} at {self.institution_name}"


class InstructorProfileInformation(models.Model):
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='profile_info')
    institution_name = models.CharField(max_length=255, blank=True, null=True)
    course = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    marks = models.CharField(max_length=100, blank=True, null=True)
    work_history_institution = models.CharField(max_length=255, blank=True, null=True)
    work_start_date = models.CharField(max_length=100, blank=True, null=True)
    work_end_date = models.CharField(max_length=100, blank=True, null=True)
    services = models.CharField(max_length=255, blank=True, null=True)
    specializations = models.CharField(max_length=255, blank=True, null=True)
    workspace_image = models.ImageField(upload_to='workspace_images/', blank=True, null=True)


    def __str__(self):
        return f"{self.instructor.user.email} - Profile Information"

    def clean(self):
        # Validation to ensure that the education end date is after the start date
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError({'end_date': 'End date must be after start date.'})

    # Override save method to ensure validation is triggered
    def save(self, *args, **kwargs):
        self.full_clean()  # Ensures the clean method is called for validation
        super().save(*args, **kwargs)



DAYS_OF_WEEK = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
]

class AvailableTimeSlot(models.Model):
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='available_times')
    day_of_week = models.CharField(max_length=9, choices=DAYS_OF_WEEK, default="")
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField(default=date.today)
    is_available = models.BooleanField(default=True)

    

    class Meta:
        unique_together = ('instructor', 'day_of_week', 'start_time', 'end_time')
        ordering = ['day_of_week', 'start_time']

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

    def __str__(self):
        return f"{self.day_of_week}: {self.start_time} - {self.end_time} ({'Available' if self.is_available else 'Not Available'})"