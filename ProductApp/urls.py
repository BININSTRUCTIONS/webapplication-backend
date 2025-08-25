from django.urls import path
from . import views


urlpatterns = [
    path("download/", views.download_file),
    path("saas-product/get", views.get_saas_products),
    path("saas-product/plans/get", views.get_plan_for_saas_product),
    path("saas-product/plans/activate", views.activate_plan),
    path("saas-product/plans/activated/get", views.get_activated_plans),
    path("payment-status/notify", views.handle_payment_notification),
    path("payment-status/notifications/get", views.get_payment_notifications),

    path("realtag/reserve-spot", views.reserve_spot_for_realtag),

    path("carre/early_access/register", views.assign_for_early_access, {"productName": "CARRE"}),
    path("carre/demo/register", views.book_a_demo, {"productName": "CARRE"}),

    path("early-adoptions/get", views.get_early_adoptions),
    path("demo-requests/get", views.get_demo_requests),
    path("demo-request/edit", views.edit_demo_request),
]
