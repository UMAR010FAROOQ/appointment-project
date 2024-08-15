# models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from core.models import Service

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    profile_image_url = models.URLField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            profile = self.instructorprofile
            if self.is_active != profile.is_active:
                profile.is_active = self.is_active
                profile.save()
        except InstructorProfile.DoesNotExist:
            pass

class SimpleUserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # Add any additional fields specific to simple users

    def __str__(self):
        return f'{self.user.email} - Simple User'

class InstructorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)  # Default to inactive until approved by super admin
    city = models.CharField(max_length=100)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    # Add any additional fields specific to instructors

    def __str__(self):
        return f'{self.user.email} - Instructor'
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.user.is_active != self.is_active:
            self.user.is_active = self.is_active
            self.user.save()
