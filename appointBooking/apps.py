from django.apps import AppConfig


class AppointbookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appointBooking'

    def ready(self):
        import appointBooking.signals