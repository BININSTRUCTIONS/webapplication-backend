from django.urls import path
from . import views


urlpatterns = [
    path("key-manager/generate-api-key", views.generate_key_manager_api_key),
    path("key-manager/get-api-keys", views.get_api_keys),
    path("key-manager/get-key-information", views.get_key_manager_key_information),
    path("key-manager/activate-key", views.activate_key),
    path("key-manager/mark-key-as-active", views.mark_key_as_active),
]