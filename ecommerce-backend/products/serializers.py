from rest_framework import serializers
from .models import Category, Product, ProductImage, Review


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    children = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(
        source='products.count',
        read_only=True
    )
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 
            'parent', 'children', 'product_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        """Get child categories."""
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for Product Images."""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'is_primary', 'display_order']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Product Reviews."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'user', 'user_email', 'user_name',
            'rating', 'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(
        source='reviews.count',
        read_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'category_name',
            'primary_image', 'is_in_stock', 'average_rating',
            'review_count', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Get primary product image."""
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return ProductImageSerializer(primary).data
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image).data
        return None
    
    def get_average_rating(self, obj):
        """Calculate average rating."""
        reviews = obj.reviews.all()
        if reviews.exists():
            total = sum(review.rating for review in reviews)
            return round(total / reviews.count(), 1)
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product view."""
    
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(
        source='reviews.count',
        read_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price',
            'category', 'category_id', 'stock_quantity', 'sku',
            'is_active', 'is_in_stock', 'images', 'reviews',
            'average_rating', 'review_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        """Calculate average rating."""
        reviews = obj.reviews.all()
        if reviews.exists():
            total = sum(review.rating for review in reviews)
            return round(total / reviews.count(), 1)
        return None


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products."""
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'category',
            'stock_quantity', 'sku', 'is_active'
        ]
    
    def validate_sku(self, value):
        """Validate SKU is unique."""
        if self.instance:
            # Update case
            if Product.objects.exclude(pk=self.instance.pk).filter(sku=value).exists():
                raise serializers.ValidationError("Product with this SKU already exists.")
        else:
            # Create case
            if Product.objects.filter(sku=value).exists():
                raise serializers.ValidationError("Product with this SKU already exists.")
        return value