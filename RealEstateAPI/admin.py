from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([
    City,
    State,
    Country,
    Agent,
    RealEstate,
    House,
    Land,
    EstateStatus,
    PropertyMedia
])
