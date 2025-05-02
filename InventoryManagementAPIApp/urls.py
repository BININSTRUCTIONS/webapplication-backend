from django.urls import path
from .views import *

urlpatterns = [
    path("register", register_business),
    path("types", get_business_types),
    path("get", get_business),
]
