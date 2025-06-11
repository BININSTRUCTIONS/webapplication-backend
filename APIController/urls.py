from django.urls import path
from . import views


urlpatterns = [
    # generate an API key
    path("key-manager/generate-api-key", views.generate_key_manager_api_key),

    # Get all API keys
    path("key-manager/get-api-keys", views.get_api_keys),
    
    # # Get information of a specific key
    # path("key-manager/get-key-information", views.get_key_manager_key_information),

    # # Increase the activation count. (Used time)
    # path("key-manager/activate-key", views.activate_key),

    # # Mark the key as active. (Valid to use)
    # path("key-manager/mark-key-as-active", views.mark_key_as_active),
]