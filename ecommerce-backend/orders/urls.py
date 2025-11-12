from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CartViewSet

app_name = 'orders'

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('cart/', CartViewSet.as_view({'get': 'list'}), name='cart'),
    path('cart/add/', CartViewSet.as_view({'post': 'add'}), name='cart-add'),
    path('cart/update/<int:item_id>/', CartViewSet.as_view({'patch': 'update_item'}), name='cart-update'),
    path('cart/remove/<int:item_id>/', CartViewSet.as_view({'delete': 'remove_item'}), name='cart-remove'),
    path('cart/clear/', CartViewSet.as_view({'delete': 'clear'}), name='cart-clear'),
]