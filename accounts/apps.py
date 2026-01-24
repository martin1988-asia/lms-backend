from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Learning Management - Accounts"

    def ready(self):
        """
        Import signals when the app is ready.
        Ensures profile creation/updates are hooked automatically.
        """
        import accounts.models  # noqa
