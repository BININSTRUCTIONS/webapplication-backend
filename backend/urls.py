"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from django.conf import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="eyecareaboutcredit API",
      default_version='v1',
      description="",
    #   terms_of_service="https://www.yourapp.com/terms/",
    #   contact=openapi.Contact(email="contact@yourapp.com"),
    #   license=openapi.License(name="Your License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls")),
    path("api/v1/customer-service/", include("CustomerService.urls")),
    path("api/v1/saas-platform/key-manager/", include("KeyManager.urls")),
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    path("api/business/real-estate/", include("RealEstateAPI.urls")),
    path("api/business/", include("InventoryManagementAPIApp.urls")),
    path("api/v1/apis/", include("APIs.urls")),
    path("api/v1/api-keys/", include("APIController.urls")),
    path("api/v1/product/", include('ProductApp.urls')),
    path("api/v1/partners/", include('Partners.urls')),
    path('swagger<str:format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
