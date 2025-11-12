from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Q
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    ReviewSerializer
)
from .filters import ProductFilter


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for categories.
    
    GET /api/categories/ - List all categories
    POST /api/categories/ - Create category (admin only)
    GET /api/categories/{id}/ - Retrieve category
    PUT/PATCH /api/categories/{id}/ - Update category (admin only)
    DELETE /api/categories/{id}/ - Delete category (admin only)
    """
    queryset = Category.objects.prefetch_related('children', 'products')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Get all products in a category."""
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            is_active=True
        ).select_related('category').prefetch_related('images', 'reviews')
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for products with advanced filtering, sorting, and pagination.
    
    GET /api/products/ - List products (with filtering, sorting, pagination)
    POST /api/products/ - Create product (admin only)
    GET /api/products/{id}/ - Retrieve product details
    PUT/PATCH /api/products/{id}/ - Update product (admin only)
    DELETE /api/products/{id}/ - Delete product (admin only)
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'name', 'stock_quantity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Optimize queryset with select_related and prefetch_related."""
        queryset = Product.objects.select_related('category').prefetch_related(
            'images', 'reviews'
        )
        
        # Show only active products to non-staff users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        """Get all reviews for a product."""
        product = self.get_object()
        reviews = product.reviews.select_related('user').order_by('-created_at')
        
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced search endpoint.
        
        Query params:
        - q: search query
        - min_price: minimum price
        - max_price: maximum price
        - category: category id
        """
        queryset = self.get_queryset()
        
        # Search query
        query = request.query_params.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(sku__icontains=query)
            )
        
        # Price range
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Category filter
        category_id = request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for product reviews.
    
    GET /api/reviews/ - List all reviews
    POST /api/reviews/ - Create review (authenticated users only)
    GET /api/reviews/{id}/ - Retrieve review
    PUT/PATCH /api/reviews/{id}/ - Update review (owner only)
    DELETE /api/reviews/{id}/ - Delete review (owner only)
    """
    queryset = Review.objects.select_related('user', 'product')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Set the user when creating a review."""
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        """Filter reviews by product if specified."""
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset