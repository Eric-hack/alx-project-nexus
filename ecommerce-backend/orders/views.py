from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Order, Cart, CartItem
from products.models import Product
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for orders.
    
    GET /api/orders/ - List user's orders
    POST /api/orders/ - Create new order
    GET /api/orders/{id}/ - Retrieve order details
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return orders for the current user."""
        user = self.request.user
        queryset = Order.objects.prefetch_related('items__product')
        
        # Staff can see all orders, regular users only their own
        if not user.is_staff:
            queryset = queryset.filter(user=user)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        return OrderDetailSerializer
    
    def perform_create(self, serializer):
        """Set the user when creating an order."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """Cancel an order."""
        order = self.get_object()
        
        if order.status in ['delivered', 'cancelled']:
            return Response({
                'error': f'Cannot cancel order with status: {order.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Restore stock
        for item in order.items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.save()
        
        order.status = 'cancelled'
        order.save()
        
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)


class CartViewSet(viewsets.ViewSet):
    """
    API endpoint for shopping cart operations.
    
    GET /api/cart/ - Get current cart
    POST /api/cart/add/ - Add item to cart
    PATCH /api/cart/update/{item_id}/ - Update cart item quantity
    DELETE /api/cart/remove/{item_id}/ - Remove item from cart
    DELETE /api/cart/clear/ - Clear entire cart
    """
    permission_classes = [IsAuthenticated]
    
    def get_or_create_cart(self, user):
        """Get or create cart for user."""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    def list(self, request):
        """Get user's cart."""
        cart = self.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add(self, request):
        """Add item to cart."""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = self.get_or_create_cart(request.user)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({
                'error': 'Product not found or inactive'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check stock
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # Verify stock availability
        if cart_item.quantity > product.stock_quantity:
            return Response({
                'error': f'Insufficient stock. Available: {product.stock_quantity}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Item added to cart',
            'cart': CartSerializer(cart).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['patch'], url_path='update/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """Update cart item quantity."""
        try:
            cart = self.get_or_create_cart(request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({
                'error': 'Cart item not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        quantity = request.data.get('quantity')
        if not quantity or quantity < 1:
            return Response({
                'error': 'Quantity must be at least 1'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check stock
        if quantity > cart_item.product.stock_quantity:
            return Response({
                'error': f'Insufficient stock. Available: {cart_item.product.stock_quantity}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return Response({
            'message': 'Cart item updated',
            'cart': CartSerializer(cart).data
        })
    
    @action(detail=False, methods=['delete'], url_path='remove/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """Remove item from cart."""
        try:
            cart = self.get_or_create_cart(request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({
                'error': 'Cart item not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'message': 'Item removed from cart',
            'cart': CartSerializer(cart).data
        })
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from cart."""
        cart = self.get_or_create_cart(request.user)
        cart.items.all().delete()
        
        return Response({
            'message': 'Cart cleared',
            'cart': CartSerializer(cart).data
        })