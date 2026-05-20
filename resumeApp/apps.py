from django.apps import AppConfig
class resumeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'resumeApp'

    def ready(self):
        import resumeApp.signals