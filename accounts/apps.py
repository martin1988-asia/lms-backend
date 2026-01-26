from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuration for the Accounts app.
    Ensures signals are loaded and provides a clear verbose name.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Learning Management - Accounts"

    def ready(self):
        """
        Import signals when the app is ready.
        Keeps signal logic separate from models to avoid circular imports.
        """
        import accounts.signals  # noqa
