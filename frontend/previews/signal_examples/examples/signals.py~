from django.dispatch import receiver
from django.db.models.signals import (post_save)
from .models import Book, AuthorBalance


@receiver(post_save, sender=Book)
def credit_author(sender, instance, *args, **kwargs):
    if instance.active and not instance.credited_at:
        balance = AuthorBalance.objects.get_or_create(
            publisher=instance.publisher,
            author=instance.author)
        balance.value += instance.value
        balance.save()
