# Django
from django.contrib import admin

# Custom
from .models import Note, Category, NotepikUser


# Register your models here.
# This is for admin page where you can edit, add, delete, etc models
admin.site.register(Note)
admin.site.register(Category)
admin.site.register(NotepikUser)
