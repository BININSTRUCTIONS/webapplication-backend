from django.urls import path
from . import views


urlpatterns = [
    path("download/", views.download_file),
    path("saas-product/get", views.get_saas_products),
    path("saas-product/plans/get", views.get_plan_for_saas_product),
    path("saas-product/plans/activate", views.activate_plan),
    path("saas-product/plans/activated/get", views.get_activated_plans),
]
