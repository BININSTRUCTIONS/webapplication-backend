from django.urls import path
from . import views

urlpatterns = [
    path("get-keys", views.get_key_manager_keys),
    path("add-key", views.add_key_manager_key),
    path("change-key", views.change_key_manager_key),
    path("plans/activate", views.activate_plan),
    path("data", views.get_key_manager_data),


    # Get information of a specific key
    path("get-key-information", views.get_key_manager_key_information),

    # Increase the activation count. (Used time)
    path("activate-key", views.activate_key),

    # Mark the key as active. (Valid to use)
    path("mark-key-as-active", views.mark_key_as_active),

    # Delete the key
    path("delete-key", views.delete_key),
]