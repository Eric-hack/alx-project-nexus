from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product, ProductImage
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Create sample users
        self.stdout.write('Creating users...')
        if not User.objects.filter(email='admin@example.com').exists():
            User.objects.create_superuser(
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
        
        if not User.objects.filter(email='user@example.com').exists():
            User.objects.create_user(
                email='user@example.com',
                password='user123',
                first_name='Test',
                last_name='User'
            )
        
        # Create categories
        self.stdout.write('Creating categories...')
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'description': 'Fashion and apparel'},
            {'name': 'Books', 'description': 'Physical and digital books'},
            {'name': 'Home & Garden', 'description': 'Home improvement and garden supplies'},
            {'name': 'Sports', 'description': 'Sports equipment and accessories'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'  Created category: {category.name}')
        
        # Create products
        self.stdout.write('Creating products...')
        products_data = [
            # Electronics
            {'name': 'Wireless Headphones', 'category': 0, 'price': 79.99, 'stock': 50},
            {'name': 'Smart Watch', 'category': 0, 'price': 199.99, 'stock': 30},
            {'name': 'Laptop Stand', 'category': 0, 'price': 34.99, 'stock': 100},
            {'name': 'USB-C Hub', 'category': 0, 'price': 29.99, 'stock': 75},
            
            # Clothing
            {'name': 'Cotton T-Shirt', 'category': 1, 'price': 19.99, 'stock': 200},
            {'name': 'Denim Jeans', 'category': 1, 'price': 49.99, 'stock': 150},
            {'name': 'Running Shoes', 'category': 1, 'price': 89.99, 'stock': 80},
            
            # Books
            {'name': 'Python Programming Guide', 'category': 2, 'price': 39.99, 'stock': 60},
            {'name': 'Web Development Handbook', 'category': 2, 'price': 44.99, 'stock': 45},
            
            # Home & Garden
            {'name': 'LED Desk Lamp', 'category': 3, 'price': 24.99, 'stock': 90},
            {'name': 'Plant Pot Set', 'category': 3, 'price': 15.99, 'stock': 120},
            
            # Sports
            {'name': 'Yoga Mat', 'category': 4, 'price': 29.99, 'stock': 110},
            {'name': 'Resistance Bands Set', 'category': 4, 'price': 19.99, 'stock': 95},
        ]
        
        for idx, prod_data in enumerate(products_data, 1):
            product, created = Product.objects.get_or_create(
                sku=f'SKU-{idx:05d}',
                defaults={
                    'name': prod_data['name'],
                    'description': f"High-quality {prod_data['name'].lower()} for everyday use.",
                    'price': Decimal(str(prod_data['price'])),
                    'category': categories[prod_data['category']],
                    'stock_quantity': prod_data['stock'],
                    'is_active': True,
                }
            )
            
            if created:
                # Add sample image
                ProductImage.objects.create(
                    product=product,
                    image_url=f'https://via.placeholder.com/400x400?text={product.name.replace(" ", "+")}',
                    alt_text=product.name,
                    is_primary=True,
                    display_order=0
                )
                self.stdout.write(f'  Created product: {product.name}')
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))