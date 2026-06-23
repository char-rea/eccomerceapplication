from django.urls import path
from shop import views

urlpatterns = [
    path("stores/", views.view_stores),
    path("stores/add/", views.create_store),
    path("stores/<int:pk>/edit/", views.api_edit_store),
    path("stores/<int:pk>/delete/", views.api_delete_store),
    path("products/", views.api_products),
    path("reviews/", views.vendor_reviews),
    path("vendor/products-with-reviews/", views.vendor_products_with_reviews),
    path("vendors/", views.vendors_with_stores_and_products),
]