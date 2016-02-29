from __future__ import unicode_literals

# Python
import logging
import datetime

# Django
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.timezone import utc

# Custom
from main.model_managers import NoteManager, CategoryManager
from main.model_managers import NotepikUserManager, EncodedUrlManager
from main.utils import get_expiration_date

logger = logging.getLogger(__name__)


class Note(models.Model):
    """
    Model for notes
    """
    note = models.CharField(max_length=2100)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    # Notes can only have one author 
    author = models.ForeignKey('NotepikUser',
            related_name="%(class)ss_created")
    # Many notes can have many keys (for reposting of notes)
    reposters = models.ManyToManyField('NotepikUser', through="NoteReposter", 
            related_name="%(class)ss_reposted", blank=True)
    # Many notes can have many categories
    categories = models.ManyToManyField('Category', blank=True, 
            related_name='notes')


    # Model manager
    objects = NoteManager()

    def __unicode__(self):
        return self.note;


    class Meta:
        ordering = ('-date_created',)


    def extract_categories(self):
        """ 
        Extract words that starts with '#' to use as categories
        and return the list of found words. if it don't have any just return an empty list
        """
        categories = list()

        for word in self.note.split():
            if word.startswith("#"):
                categories.append(word.strip('#'))

        return categories

    def save(self, *args, **kwargs):
        super(Note, self).save(*args, **kwargs)

        categories = self.extract_categories()
        old_categories = [category.category for category in self.categories.all()]
        
        # Check if there's a new category in the note
        if categories != old_categories:
            logger.debug('Note: note: {}'.format(self.note))
            logger.debug('Note: author: {}'.format(self.author.get_short_name()))
            logger.debug('Note: categories: {}'.format(categories))
            logger.debug('Note: date_modified: {}'.format(self.date_modified))
            logger.debug('Note: date_created: {}'.format(self.date_created))
            for category in categories:
                self.categories.add(Category.objects.get_or_create(category=category)[0])


class NoteReposter(models.Model):
    """
    Intermediary for m2m between notes and user (reposters)
    """
    note = models.ForeignKey("Note", on_delete=models.CASCADE)
    user = models.ForeignKey("NotepikUser", on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True, blank=True)

    # Date added to vault. The date when this user repost this note
    date_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "{} : {}".format(self.user.email, self.note.note)

    class Meta:
        verbose_name_plural = 'Note Reposters'
        ordering = ('-date_added',)


class Category(models.Model):
    """ 
    For categories mentioned in notes
    """

    category = models.CharField(unique=True, max_length=15)

    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = CategoryManager()

    def __unicode__(self):
        return self.category;

    # Lowercase the category name when saving
    def save(self, *args, **kwargs):
        self.category = self.category.lower()
        super(Category, self).save(*args, **kwargs)
        logger.debug('Category: category: {}'.format(self.category))
        logger.debug('Category: date_modified: {}'.format(self.date_modified))
        logger.debug('Category: date_created: {}'.format(self.date_created))

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('-date_created',)


class NotepikUser(AbstractBaseUser, PermissionsMixin):
    """ 
    User model
    """
    email = models.EmailField(unique=True, max_length=150)
    key = models.CharField(unique=True, max_length=100)

    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    USERNAME_FIELD = 'email'

    objects = NotepikUserManager()

    def __unicode__(self):
        return self.email

    def set_password(self, raw_password):
        self.key = raw_password
        super(NotepikUser, self).set_password(raw_password)

    def get_short_name(self):
        return self.email.split('@')[0]

    def get_full_name(self):
        return self.email

    class Meta:
        ordering = ('-date_joined',)


class EncodedUrl(models.Model):
    """ 
    Model to use as hash url in vault page
    """
    encoded_url = models.CharField(blank=False, max_length=68)
    salt = models.CharField(blank=False, max_length=68)
    user = models.ForeignKey('NotepikUser', related_name='encoded_urls')
    expiration_date = models.DateTimeField("Expiration date",
            default=get_expiration_date)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = EncodedUrlManager()

    def __unicode__(self):
        return self.user.email;

    class Meta: 
        ordering = ('-date_created',)

