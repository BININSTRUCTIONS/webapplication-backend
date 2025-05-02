from django.urls import path
from .views import *


urlpatterns = [
    path("add", add_api),
    path("update", update_api),
    path("delete", delete_api),
    path("get-all", get_apis),
    path("subscribed", get_subscribed_apis),
]
