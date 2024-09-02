# models.py
from django.db import models
from django.utils import timezone
from django.conf import settings
from authentication.models import InstructorProfile
from django.core.exceptions import ValidationError


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
    perhpur = models.IntegerField(blank=True, null=True)
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