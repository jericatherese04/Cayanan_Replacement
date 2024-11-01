from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'home'

    def ready(self):
        import home.signals


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'
