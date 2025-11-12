from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="E-Commerce API",
        default_version='v1',
        description="""
        Comprehensive E-Commerce Backend API with advanced features.
        
        ## Features
        - User Authentication (JWT)
        - Product Management with Filtering & Pagination
        - Category Management
        - Shopping Cart
        - Order Processing
        - Product Reviews
        
        ## Authentication
        Use the `/api/auth/login/` endpoint to get your access token.
        Then include it in requests: `Authorization: Bearer <your_token>`
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@ecommerce.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API Endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/', include('products.urls')),
    path('api/', include('orders.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)