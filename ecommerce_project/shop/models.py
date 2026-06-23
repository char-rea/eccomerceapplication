"""
models.py
---------
This file defines all database models for the e‑commerce application.

The models represent:
- Users and roles (Profile)
- Product categorisation (Category)
- Vendor stores
- Products
- Orders and order items
- Product reviews

Django’s ORM (Object Relational Mapper) is used to define
database tables as Python classes.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# ─────────────────────────────────────────────
# CATEGORY MODEL
# ─────────────────────────────────────────────

class Category(models.Model):
    """
    Represents a product category (e.g. Electronics, Clothing).

    Categories are used to group products and improve navigation.
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        # Orders categories alphabetically
        ordering = ['name']

        # Proper plural name in Django admin
        verbose_name_plural = 'categories'

    def __str__(self):
        # Human-readable representation
        return self.name


# ─────────────────────────────────────────────
# PROFILE MODEL
# ─────────────────────────────────────────────

class Profile(models.Model):
    """
    Extends Django’s built-in User model with role-based access.

    Each user has exactly one profile which defines whether they are:
    - a vendor (can create stores and products)
    - a buyer (can purchase and review products)
    """

    ROLE_CHOICES = [
        ('vendor', 'Vendor'),
        ('buyer', 'Buyer'),
    ]

    # One-to-one relationship with Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Role used for authorization logic
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='buyer'
    )

    def __str__(self):
        return f'{self.user.username} - {self.role}'

    # Helper methods used by decorators and views
    def is_vendor(self):
        return self.role == 'vendor'

    def is_buyer(self):
        return self.role == 'buyer'


# ─────────────────────────────────────────────
# STORE MODEL
# ─────────────────────────────────────────────

class Store(models.Model):
    """
    Represents a vendor’s store.

    Each vendor may own multiple stores.
    Each store can contain multiple products.
    """

    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stores'
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────
# PRODUCT MODEL
# ─────────────────────────────────────────────

class Product(models.Model):
    """
    Represents a product sold in the store.

    Products belong to:
    - a Store (vendor-owned)
    - optionally a Category
    """

    store = models.ForeignKey(
        Store,
        related_name='products',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=200)

    # Slug is auto-generated for SEO-friendly URLs
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Automatically generates a unique slug when the product is saved.

        If a slug already exists, a numeric suffix is added.
        Example:
        - phone
        - phone-1
        - phone-2
        """
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        # Default ordering
        ordering = ['name']

        # Improves database query performance
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]


# ─────────────────────────────────────────────
# ORDER MODELS
# ─────────────────────────────────────────────

class Order(models.Model):
    """
    Represents a customer order.

    An order belongs to one user and can have multiple order items.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):
    """
    Represents a single item within an order.
    """

    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)


# ─────────────────────────────────────────────
# REVIEW MODEL
# ─────────────────────────────────────────────

class Review(models.Model):
    """
    Represents a product review submitted by a buyer.

    Reviews can be marked as 'verified' if the user has purchased
    the product.
    """

    product = models.ForeignKey(
        Product,
        related_name='reviews',
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()

    # Indicates if the reviewer purchased the product
    verified = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Most recent reviews appear first
        ordering = ['-created']

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"