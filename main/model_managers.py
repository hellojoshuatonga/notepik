# Django
from django.db import models
from django.contrib.auth.models import UserManager
from django.contrib.auth.base_user import BaseUserManager


class NoteManager(models.Manager):
    """
    Model manager for Note model
    """
    def get_or_none(self, **kwargs):
        """ 
        Will return None if not found in database
        """
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class CategoryManager(models.Manager):
    """
    Model manager for Category model
    """
    def create(self, **kwargs):
        kwargs['category'] = kwargs.get('category').lower()
        return super(CategoryManager, self).create(**kwargs)
    def get_or_create(self, **kwargs):
        kwargs['category'] = kwargs.get('category').lower()
        return super(CategoryManager, self).get_or_create(**kwargs)
    def get_or_none(self, **kwargs):
        """ 
        Will return None if not found in database
        """
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class NotepikUserManager(BaseUserManager):
    """
    Model manager for NotepikUser model
    """
    # use_in_migrations = True

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, password=password, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, 
            **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(email, password, **extra_fields)

    def is_already_added(self, user):
        """
        Check if he/she is already in the list used in
        note reposters
        """
        already_added = self.get_or_none(key=user.key)
        if already_added:
            return True
        else:
            return False


class EncodedUrlManager(models.Manager):
    """ Model manager for EncodedUrl """
    def get_or_none(self, **kwargs):
        """ 
        Will return None if not found in database
        """
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None
