from django.urls import path
from .views import *

urlpatterns = [
    path("agent/get", agent_get),
    path("agent/add", agent_add),
    path("agent/delete", agent_delete),
    path("agent/update", agent_update),

    path("property/status/list", get_property_statuses),

    path("house/get", house_get),
    path("house/add", house_add),
    path("house/delete", house_delete),
    path("house/update", house_update),

    path("land/get", land_get),
    path("land/add", land_add),
    path("land/delete", land_delete),
    path("land/update", land_update),

    path("chat/start", start_chat),
    path("chat/get", get_chats),
    path("chat/messages/get", get_messages),
    path("chat/message/send", send_message),

    path("user/assign", assign_user_to_business),

    path("countries", get_countries),
    path("states", get_states),
]
