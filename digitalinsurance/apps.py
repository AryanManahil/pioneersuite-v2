from django.apps import AppConfig

class DigitalInsuranceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'digitalinsurance'

    def ready(self):
        # Automatically create customer profiles when users are created
        import digitalinsurance.signals
