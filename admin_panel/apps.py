from django.apps import AppConfig

class AdminPanelConfig(AppConfig):
    """
    Configuration for the admin_panel application.
    The name must match the application directory name.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_panel'

    def ready(self):
        """
        Imports the signals module so Django can register the signal handlers
        when the application is initialized.
        """
        import admin_panel.signals


from django.apps import AppConfig

class AppointmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appointments'

    def ready(self):
        import appointments.signals
