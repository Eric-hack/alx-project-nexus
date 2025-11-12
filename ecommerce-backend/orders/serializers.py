from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem
from products.models import Product
from products.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for Order Items."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_details = ProductListSerializer(source='product', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_details',
            'quantity', 'unit_price', 'subtotal'
        ]
        read_only_fields = ['subtotal']


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for listing orders."""
    
    items_count = serializers.IntegerField(
        source='items.count',
        read_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'total_amount',
            'items_count', 'created_at', 'updated_at'
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single order view."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_email', 'status',
            'total_amount', 'shipping_address', 'billing_address',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'user', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders."""
    
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'shipping_address', 'billing_address', 'items'
        ]
    
    def validate_items(self, value):
        """Validate order items."""
        if not value:
            raise serializers.ValidationError("Order must contain at least one item.")
        
        for item in value:
            if 'product_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError(
                    "Each item must have 'product_id' and 'quantity'."
                )
            
            try:
                product = Product.objects.get(id=item['product_id'], is_active=True)
                if product.stock_quantity < item['quantity']:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
                    )
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f"Product with id {item['product_id']} does not exist or is inactive."
                )
        
        return value
    
    def create(self, validated_data):
        """Create order with items."""
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Calculate total
        total_amount = 0
        order_items = []
        
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            quantity = item_data['quantity']
            unit_price = product.price
            subtotal = quantity * unit_price
            total_amount += subtotal
            
            order_items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'subtotal': subtotal
            })
        
        # Create order
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            **validated_data
        )
        
        # Create order items and update stock
        for item_data in order_items:
            OrderItem.objects.create(order=order, **item_data)
            product = item_data['product']
            product.stock_quantity -= item_data['quantity']
            product.save()
        
        return order


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for Cart Items."""
    
    product_details = ProductListSerializer(source='product', read_only=True)
    item_total = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_details', 'quantity',
            'item_total', 'added_at'
        ]
    
    def get_item_total(self, obj):
        """Calculate item total price."""
        return obj.product.price * obj.quantity
    
    def validate_quantity(self, value):
        """Validate quantity."""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Shopping Cart."""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items', 'total_items',
            'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart."""
    
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    
    def validate_product_id(self, value):
        """Validate product exists and is active."""
        try:
            product = Product.objects.get(id=value, is_active=True)
            if not product.is_in_stock:
                raise serializers.ValidationError("Product is out of stock.")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist or is inactive.")
        return value