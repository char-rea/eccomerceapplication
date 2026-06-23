from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Category model.

    - Automatically populates the slug field from the name.
    """

    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Product model.

    Features:
    - Displays key product details in the list view.
    - Allows filtering by availability, dates, and category.
    - Enables inline editing for price and availability.
    - Automatically populates the slug field from the name.
    """

    list_display = ('name', 'price', 'available', 'created', 'updated')
    list_filter = ('available', 'created', 'updated', 'category')
    list_editable = ('price', 'available')
    prepopulated_fields = {'slug': ('name',)}