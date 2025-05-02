from django.urls import path
from .views import *


urlpatterns = [
    path("init", customer_service_chat_request),
    path("message/send", send_message_to_customer_service),
    path("messages/get", get_customer_service_messages),
    path("chat/get", get_customer_service_chats),
]
