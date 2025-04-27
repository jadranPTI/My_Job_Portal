from django.contrib import admin
from .models import CustomUser, Job

admin.site.register(CustomUser)
admin.site.register(Job)

