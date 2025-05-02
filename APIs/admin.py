from django.contrib import admin

from .models import APIKey, APIInfo

# Register your models here.
admin.site.register([APIKey, APIInfo])
