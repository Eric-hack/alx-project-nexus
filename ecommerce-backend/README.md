#  E-Commerce Backend API

A robust, scalable e-commerce backend system built with Django REST Framework, featuring JWT authentication, advanced filtering, pagination, and comprehensive API documentation.

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-5.0-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 Features

### Core Functionality
-  **User Authentication & Authorization** - JWT-based secure authentication
-  **Product Management** - Full CRUD operations with images
-  **Category Management** - Hierarchical category structure
-  **Shopping Cart** - Add, update, remove items
-  **Order Processing** - Complete order workflow with status tracking
-  **Product Reviews** - User ratings and comments

### Advanced Features
-  **Advanced Search** - Multi-field search with filters
-  **Filtering & Sorting** - Filter by price, category, stock status
-  **Pagination** - Efficient data loading for large datasets
-  **Database Optimization** - Indexed queries, select_related, prefetch_related
-  **API Documentation** - Interactive Swagger/OpenAPI documentation
-  **Security** - Password validation, CORS configuration, JWT tokens

##  Architecture

### Database Schema
```
Users (Custom User Model)
├── Orders
│   └── OrderItems
├── Cart
│   └── CartItems
└── Reviews

Categories (Hierarchical)
└── Products
    ├── ProductImages
    └── Reviews
```

##  Getting Started

### Prerequisites
- Python 3.9 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Eric-hack/alx-project-nexus.git
cd ecommerce-backend
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL database**
```bash
# Access PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ecommerce_db;
CREATE USER ecommerce_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
\q
```

5. **Configure environment variables**

Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

6. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Seed database with sample data (Optional)**
```bash
python manage.py seed_data
```

9. **Run development server**
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

##  API Documentation

### Access Swagger Documentation
- **Swagger UI**: http://127.0.0.1:8000/
- **ReDoc**: http://127.0.0.1:8000/api/redoc/
- **JSON Schema**: http://127.0.0.1:8000/api/schema/

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

#### Login (Get JWT Token)
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Get User Profile
```http
GET /api/auth/profile/
Authorization: Bearer <access_token>
```

#### Update Profile
```http
PATCH /api/auth/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Jane",
  "phone": "+0987654321"
}
```

#### Change Password
```http
POST /api/auth/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!",
  "new_password2": "NewPass123!"
}
```

### Product Endpoints

#### List Products (with filtering, sorting, pagination)
```http
GET /api/products/
GET /api/products/?page=2
GET /api/products/?category=1
GET /api/products/?min_price=20&max_price=100
GET /api/products/?ordering=-price
GET /api/products/?search=laptop
GET /api/products/?in_stock=true
```

#### Get Product Details
```http
GET /api/products/{slug}/
```

#### Create Product (Admin only)
```http
POST /api/products/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse",
  "price": "29.99",
  "category": 1,
  "stock_quantity": 100,
  "sku": "MOUSE-001",
  "is_active": true
}
```

#### Update Product (Admin only)
```http
PATCH /api/products/{slug}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "price": "24.99",
  "stock_quantity": 150
}
```

#### Delete Product (Admin only)
```http
DELETE /api/products/{slug}/
Authorization: Bearer <access_token>
```

#### Advanced Search
```http
GET /api/products/search/?q=laptop&min_price=500&max_price=2000&category=1
```

### Category Endpoints

#### List Categories
```http
GET /api/categories/
```

#### Get Category Details
```http
GET /api/categories/{slug}/
```

#### Get Products in Category
```http
GET /api/categories/{slug}/products/
```

#### Create Category (Admin only)
```http
POST /api/categories/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Accessories",
  "description": "Tech accessories",
  "parent": null
}
```

### Shopping Cart Endpoints

#### Get Cart
```http
GET /api/cart/
Authorization: Bearer <access_token>
```

#### Add Item to Cart
```http
POST /api/cart/add/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}
```

#### Update Cart Item
```http
PATCH /api/cart/update/{item_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "quantity": 3
}
```

#### Remove Item from Cart
```http
DELETE /api/cart/remove/{item_id}/
Authorization: Bearer <access_token>
```

#### Clear Cart
```http
DELETE /api/cart/clear/
Authorization: Bearer <access_token>
```

### Order Endpoints

#### List Orders
```http
GET /api/orders/
Authorization: Bearer <access_token>
GET /api/orders/?status=pending
GET /api/orders/?ordering=-created_at
```

#### Get Order Details
```http
GET /api/orders/{id}/
Authorization: Bearer <access_token>
```

#### Create Order
```http
POST /api/orders/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "shipping_address": "123 Main St, City, Country",
  "billing_address": "123 Main St, City, Country",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 3,
      "quantity": 1
    }
  ]
}
```

#### Cancel Order
```http
PATCH /api/orders/{id}/cancel/
Authorization: Bearer <access_token>
```

### Review Endpoints

#### List Reviews
```http
GET /api/reviews/
GET /api/reviews/?product_id=1
GET /api/reviews/?rating=5
```

#### Get Product Reviews
```http
GET /api/products/{slug}/reviews/
```

#### Create Review
```http
POST /api/reviews/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "product": 1,
  "rating": 5,
  "comment": "Excellent product!"
}
```

#### Update Review
```http
PATCH /api/reviews/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "rating": 4,
  "comment": "Good product, updated review"
}
```

#### Delete Review
```http
DELETE /api/reviews/{id}/
Authorization: Bearer <access_token>
```

##  Authentication

This API uses JWT (JSON Web Tokens) for authentication.

### How to Authenticate

1. **Register** or **Login** to get access and refresh tokens
2. Include the access token in the Authorization header:
   ```
   Authorization: Bearer <your_access_token>
   ```
3. When the access token expires, use the refresh token to get a new one:
   ```http
   POST /api/auth/token/refresh/
   Content-Type: application/json

   {
     "refresh": "<your_refresh_token>"
   }
   ```

##  Database Optimization

### Indexes
The following fields are indexed for optimal query performance:
- User: `email`
- Product: `slug`, `sku`, `category`, `is_active`, `price`, `created_at`
- Category: `slug`, `parent`
- Order: `order_number`, `user`, `status`, `created_at`

### Query Optimization
- `select_related()` for foreign key relationships
- `prefetch_related()` for reverse foreign key and many-to-many relationships
- Database-level constraints for data integrity

##  Technologies Used

- **Framework**: Django 5.0, Django REST Framework 3.14
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API Documentation**: drf-yasg (Swagger/OpenAPI)
- **Filtering**: django-filter
- **CORS**: django-cors-headers
- **Production Server**: Gunicorn
- **Static Files**: WhiteNoise

##  Project Structure

```
ecommerce-backend/
├── accounts/              # User authentication & management
│   ├── models.py         # Custom User model
│   ├── serializers.py    # User serializers
│   ├── views.py          # Auth endpoints
│   └── urls.py           # Auth routes
├── products/             # Product & Category management
│   ├── models.py         # Product, Category, Review models
│   ├── serializers.py    # Product serializers
│   ├── views.py          # Product endpoints
│   ├── filters.py        # Custom filters
│   ├── urls.py           # Product routes
│   └── management/       # Management commands
│       └── commands/
│           └── seed_data.py
├── orders/               # Order & Cart management
│   ├── models.py         # Order, Cart models
│   ├── serializers.py    # Order serializers
│   ├── views.py          # Order endpoints
│   └── urls.py           # Order routes
├── config/               # Project configuration
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── .env                  # Environment variables
├── .gitignore           # Git ignore file
├── requirements.txt     # Python dependencies
├── manage.py            # Django management script
└── README.md            # Project documentation
```

##  Testing

### Run Tests
```bash
python manage.py test
```

### Test Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

##  Deployment

### Prepare for Production

1. **Update settings for production**
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
```

2. **Collect static files**
```bash
python manage.py collectstatic --no-input
```

3. **Run with Gunicorn**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Deployment Platforms

#### Render
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn config.wsgi:application`
5. Add environment variables from `.env`

#### Railway
1. Create a new project on Railway
2. Connect your GitHub repository
3. Add PostgreSQL database
4. Set environment variables
5. Deploy automatically

#### Heroku
```bash
# Install Heroku CLI and login
heroku login
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False

# Deploy
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

##  Sample Data

To populate the database with sample data:

```bash
python manage.py seed_data
```

This creates:
- 2 users (admin and regular user)
- 5 categories
- 13 products with images
- Test credentials:
  - Admin: `admin@example.com` / `admin123`
  - User: `user@example.com` / `user123`

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

##  Git Workflow

```bash
# Feature commits
git commit -m "feat: add product filtering"
git commit -m "feat: implement cart functionality"

# Bug fixes
git commit -m "fix: resolve authentication issue"

# Performance improvements
git commit -m "perf: optimize database queries"

# Documentation
git commit -m "docs: update API documentation"
```

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Author

**Your Name**
- GitHub: [@Eric-hack](https://github.com/Eric-hack)
- Email: erickobbyhackman2002@gmail.com

##  Acknowledgments

- Django Documentation
- Django REST Framework
- ProDev Backend Program

##  Support

For support, email erickobbyhackman2002@gmail.com.com or create an issue in the repository.

---

**Built with ❤️ using Django REST Framework**
