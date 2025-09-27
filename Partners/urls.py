from django.urls import path
from .views import *

urlpatterns = [
    path("products/amplora/waiting-list/adduser", joinWaitingList, {"productName": "Amplora"}),
    path("products/amplora/message/send", sendMessage, {"productName": "Amplora"}),
    path("products/amplora/plans", getPlans, {"productName": "Amplora"}),
    path("products/payment-status/notify", handlePartnershipProductPaymentNotification)
]