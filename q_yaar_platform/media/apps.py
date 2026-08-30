from django.apps import AppConfig


class MediaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "media"

    def ready(self):
        # Import so the post_delete receiver is registered.
        from . import signals  # noqa: F401
