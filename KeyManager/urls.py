from django.urls import path
from . import views

urlpatterns = [
    path("get-keys", views.get_key_manager_keys),
    path("add-key", views.add_key_manager_key),
    path("change-key", views.change_key_manager_key),
    path("plans/activate", views.activate_plan),
    path("data", views.get_key_manager_data),
]