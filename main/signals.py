# Python
import logging

# Django
from django.db.models import signals
from django.dispatch import receiver

# Custom
from .models import Note, Category

logger = logging.getLogger(__name__)


# @receiver(signals.post_save, sender=Note)
# def extract_and_save_categories(sender, instance, **kwargs):
    # categories = instance.extract_categories()
    # categories_model = list()

    # if categories:
        # for category in categories:
            # # category_model = Category.objects.get_or_create(category=category)[0]
            # # logger.debug('Category: {}'.format(category_model))
            # instance.categories.add(Category.objects.get_or_create(category=category)[0])
            # logger.debug('Categories in instance: {}'.format(instance.categories.all()))
    # Note.objects.filter(pk=instance.pk).update(categories)
