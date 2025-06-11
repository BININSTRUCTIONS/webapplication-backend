from django.urls import path
from . import views

urlpatterns = [
    path("user/authenticate/signin", views.logIn),
    path("user/authenticate/signup", views.register, name="register_user"),
    path("user/authenticate/reset_password", views.password_reset),

    path("user/project/request", views.place_order),
    path("user/projects", views.get_orders),
    path("user/projects/chat/get_discussions", views.get_project_discussions),
    path("user/projects/chat/get_discussion/all", views.get_all_discussions),
    path("chat/get/project/active", views.get_project_chat),
    path("chat/set/project/active", views.uploadMessage),
    path("user/information/get", views.get_user_information),
    path("users/information", views.get_all_users_information),
    path("subscriptions/get", views.get_payhere_subscriptions),
    
    path("admin/authenticate", views.authenticate_admin),

    path("admin/projects/get/all", views.get_all_projects),
    path('admin/project/duration', views.set_project_duration),
    path("admin/project/approve", views.approve_project),
    path("admin/project/update", views.update_project),

    path("admin/products/add", views.add_product),
    path("admin/product/update/add", views.add_product_update),
    path("admin/employees/get/all", views.get_all_employees),
    path("admin/projects/action/assign/employees", views.assign_employees),
    path("admin/projects/action/get/employees", views.get_employees_for_project),
    path("admin/projects/payment/link/add", views.add_payment_link_to_project),
    path("admin/product/saas-product/add", views.add_saas_product),
    path("admin/product/saas-product/plans/edit", views.edit_saas_plan),
    path("admin/product/saas-product/plans/add", views.set_plan_for_saas_product),
    path("admin/product/saas-product/plan/item/delete", views.delete_plan_item),
    path("admin/product/saas-product/plan/item/add", views.add_plan_item),
    path("admin/product/saas-product/plans", views.get_plans),
    path("admin/product/saas-product/api-info/set", views.set_api_info_for_plan),
    path("admin/password-reset-emails/get", views.get_password_reset_email),
    
    path("user/product/payment/complete", views.complete_order),
    path("user/orders/license/keys/get/all", views.get_license_keys),
    path("user/orders/license/key/validate", views.validate_license),
    path("user/apis/subscribed", views.get_subscribed_apis),
    path("user/payment-receipts/get", views.get_payment_receipts),

    path("products/get/all", views.get_all_products),
    path("product/download", views.download_file),
    path("product/purchase", views.purchase_product),
    path("product/fetch/latest", views.get_latest_product),
    path("product/fetch/updates", views.get_product_updates),
    path("product/updates/check", views.check_product_update),
    
    path("application/types", views.get_application_types),
    path("pricing/plans", views.get_price_plans),

    path("staff/chat/projects/", views.get_staff_project_chat),

    path("anonymous/subscribe-to-newsletter", views.subscribe_to_newsletter),
]
