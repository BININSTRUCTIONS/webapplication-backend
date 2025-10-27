from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("admin/messages", consumers.MessagesConsumer.as_asgi()),
    path("admin/notification", consumers.NotificationConsumer.as_asgi())
]
