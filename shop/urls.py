"""
urls.py
-------
This file defines all URL routes for the 'shop' application.

It maps URL patterns to view functions or class-based views,
allowing users to navigate the application.

The file follows Django’s URL dispatcher system and supports:
- Authentication and password recovery
- Vendor dashboards and store management
- Product browsing and purchasing
- Cart, checkout, and reviews
"""

from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

# Application namespace used for URL reversing
app_name = "shop"


urlpatterns = [

    # ==================================================
    # AUTHENTICATION ROUTES
    # ==================================================

    # User registration (custom view)
    path('register/', views.register, name='register'),

    # User login (Django built-in authentication view)
    path('login/', auth_views.LoginView.as_view(), name='login'),

    # --------------------------------------------------
    # PASSWORD RESET FLOW (Django built-in views)
    # --------------------------------------------------
    # Step 1: User submits email for password reset
    path(
        'reset-password/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html'
        ),
        name='password_reset'
    ),

    # Step 2: Confirmation that reset email was sent
    path(
        'reset-password/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    # Step 3: Password reset confirmation using token
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    # Step 4: Password reset completion message
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),


    # ==================================================
    # VENDOR DASHBOARD
    # ==================================================

    # Main vendor dashboard page
    path('vendor/', views.vendor_dashboard, name='vendor_dashboard'),


    # ==================================================
    # STORE MANAGEMENT (VENDOR ONLY)
    # ==================================================

    # Create a new store
    path('vendor/stores/add/', views.create_store, name='store_create'),

    # Edit an existing store (identified by primary key)
    path('vendor/stores/<int:pk>/edit/', views.edit_store, name='store_edit'),

    # Delete an existing store
    path('vendor/stores/<int:pk>/delete/', views.delete_store, name='store_delete'),


    # ==================================================
    # STORE PRODUCTS (VENDOR)
    # ==================================================

    # View all products belonging to a specific store
    path(
        'vendor/stores/<int:pk>/products/',
        views.store_products,
        name='store_products'
    ),

    # Add a new product to a specific store
    path(
        'vendor/stores/<int:pk>/products/add/',
        views.create_product,
        name='product_create'
    ),


    # ==================================================
    # PRODUCT MANAGEMENT (VENDOR)
    # ==================================================

    # Edit a product
    path(
        'vendor/products/<int:pk>/edit/',
        views.edit_product,
        name='product_edit'
    ),

    # Delete a product
    path(
        'vendor/products/<int:pk>/delete/',
        views.delete_product,
        name='product_delete'
    ),


    # ==================================================
    # CART & CHECKOUT
    # ==================================================

    # View cart contents
    path('cart/', views.cart_detail, name='cart_detail'),

    # Add a product to the cart
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),

    # Remove a product from the cart
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    # Checkout and order creation
    path('checkout/', views.checkout, name='checkout'),


    # ==================================================
    # SHOP (PUBLIC / AUTHENTICATED USERS)
    # ==================================================

    # Home page
    path('', views.home, name='home'),

    # List all products
    path('products/', views.product_list, name='product_list'),

    # Product detail page using slug for SEO-friendly URLs
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),

    # Add a review to a product
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),


    # ==================================================
    # API
    # ==================================================

    # Add a path for API
    path('reddit/', views.reddit_feed, name='reddit_feed'),
    path("api/", include("shop.api.urls")),

]