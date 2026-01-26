from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create or update Profile when a CustomUser is created/updated.
    - On creation: ensures a Profile is created for the new user.
    - On update: saves the existing Profile if it exists.
    """
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, "profile"):
            instance.profile.save()
