"""
views.py
--------
This file contains all view logic for the e‑commerce application.
It handles:
- Authentication (register, login, logout)
- Product browsing
- Vendor management (stores & products)
- Buyer features (orders, cart, reviews)
- Checkout and email confirmation

The views follow Django’s MVT (Model–View–Template) architecture.
"""

from multiprocessing import context  

# Django authentication & authorization
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# Django utilities
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

# Custom role-based access decorators
from .decorators import vendor_required, buyer_required

# Forms
from .forms import UserRegisterForm, StoreForm, ProductForm, ReviewForm, RegisterForm

# Models
from .models import Product, Store, Order, OrderItem, Review, Profile

# Shopping cart session handler
from .cart import Cart
from . import models

#API
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import permission_classes
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer
import requests


# ─────────────────────────────────────────────
# AUTHENTICATION VIEWS
# ─────────────────────────────────────────────

def register(request):
    """
    Handles user registration.

    - Accepts username, password and role (vendor or buyer)
    - Prevents duplicate usernames
    - Creates a User and associated Profile with a role
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            role = request.POST.get('role')

            if role not in ('vendor', 'buyer'):
                messages.error(request, 'Invalid role selected.')
                return redirect('shop:register')

            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()

            Profile.objects.create(user=user, role=role)

            messages.success(request, 'Registration successful! Please log in.')
            return redirect('shop:login')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """
    Authenticates and logs a user into the system.
    """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            return render(request, "shop/product/list.html", context)

    return render(request, "login.html")


def logout_view(request):
    """
    Logs the user out and redirects to login page.
    """
    logout(request)
    return redirect('shop:login')


# ─────────────────────────────────────────────
# GENERAL VIEWS
# ─────────────────────────────────────────────

@login_required(login_url='login')
def home(request):
    """
    Displays the home page.
    Accessible only to logged-in users.
    """
    return render(request, 'shop/home.html')


@login_required
def product_list(request):
    """
    Displays a list of all products.
    """
    products = Product.objects.all()
    return render(request, "shop/product/list.html", {"products": products})


@login_required(login_url="login")
def product_detail(request, slug):
    """
    Displays a single product based on slug.
    """
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'shop/product/detail.html', {'product': product})


@login_required(login_url="login")
def store_products(request, pk):
    """
    Displays all products belonging to a specific store.
    """
    store = get_object_or_404(Store, pk=pk)
    products = store.products.all()

    return render(request, "vendor/store_products.html", {
        "store": store,
        "products": products,
    })


# ─────────────────────────────────────────────
# VENDOR VIEWS
# ─────────────────────────────────────────────

@login_required(login_url='/login/')
@vendor_required
def vendor_dashboard(request):
    """
    Vendor dashboard displaying all stores owned by the vendor.
    """
    stores = Store.objects.filter(owner=request.user)
    return render(request, 'vendor/dashboard.html', {'stores': stores})


@login_required(login_url='/login/')
@vendor_required
def create_store(request):
    """Regular HTML form view — no @api_view decorator"""
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            return redirect('shop:vendor_dashboard')
    else:
        form = StoreForm()
    return render(request, 'vendor/store_form.html', {'form': form})


@login_required(login_url='/login/')
@vendor_required
def create_product(request, pk):
    """
    Allows vendors to add products to their store.
    """
    store = get_object_or_404(Store, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()

            messages.success(
                request,
                f"Product '{product.name}' added successfully."
            )

            return redirect("shop:store_products", pk=store.pk)
    else:
        form = ProductForm()

    return render(request, "shop/create_product.html", {
        "form": form,
        "store": store,
    })

@login_required
def vendor_list(request):
    vendors = User.objects.filter(profile__role='vendor')
    return render(request, "shop/vendor_list.html", {"vendors": vendors})


@login_required
def vendor_stores(request, vendor_id):
    vendor = get_object_or_404(User, id=vendor_id, profile__role='vendor')
    stores = Store.objects.filter(owner=vendor)

    return render(request, "shop/vendor_stores.html", {
        "vendor": vendor,
        "stores": stores
    })

# ─────────────────────────────────────────────
# BUYER VIEWS
# ─────────────────────────────────────────────

@login_required(login_url='/login/')
@buyer_required
def buyer_dashboard(request):
    """
    Displays the buyer's order history.
    """
    orders = Order.objects.filter(user=request.user)
    return render(request, 'shop/buyer_dashboard.html', {'orders': orders})


# ─────────────────────────────────────────────
# CART VIEWS
# ─────────────────────────────────────────────

@login_required(login_url='login')
@require_POST
def cart_add(request, product_id):
    """
    Adds a product to the shopping cart.
    """
    cart = Cart(request)
    product = get_object_or_404(models.Product, id=product_id)
    cart.add(product=product)
    return redirect('shop:cart_detail')


@login_required(login_url='login')
def cart_detail(request):
    """
    Displays the contents of the shopping cart.
    """
    cart = Cart(request)
    return render(request, 'shop/cart_detail.html', {'cart': cart})


@login_required(login_url='login')
def cart_remove(request, product_id):
    """
    Removes a product from the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(models.Product, id=product_id)
    cart.remove(product)
    return redirect('shop:cart_detail')


# ─────────────────────────────────────────────
# ORDER / CHECKOUT
# ─────────────────────────────────────────────

@login_required(login_url='login')
def checkout(request):
    """
    Creates an order from the cart and sends confirmation email.
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('shop:product_list')

    order = Order.objects.create(user=request.user)

    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            price=item['price'],
            quantity=item['quantity']
        )

    cart.clear()

    send_mail(
        subject=f'Order #{order.id} Confirmation',
        message=f'Thank you for your order #{order.id}.',
        from_email='noreply@shop.com',
        recipient_list=[request.user.email],
        fail_silently=True
    )

    return render(request, 'shop/checkout_success.html', {'order': order})


# ─────────────────────────────────────────────
# REVIEWS
# ─────────────────────────────────────────────

@login_required(login_url='/login/')
def add_review(request, product_id):
    """
    Allows buyers to submit reviews.
    Reviews are marked as 'verified' if the user purchased the product.
    """
    product = get_object_or_404(models.Product, id=product_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.verified = user_has_purchased(request.user, product)
            review.save()
            return redirect('shop:product_detail', slug=product.slug)
    else:
        form = ReviewForm()

    return render(request, 'shop/add_review.html', {'form': form, 'product': product})


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def user_has_purchased(user, product):
    """
    Returns True if the user has purchased the given product.
    Used to verify reviews.
    """
    return OrderItem.objects.filter(
        order__user=user,
        product=product
    ).exists()


# ─────────────────────────────────────────────
# PRODUCTS
# ─────────────────────────────────────────────

def edit_product(request, pk):
    """
    Edit Product
    """
    product = get_object_or_404(Product, pk=pk)
    store_pk = product.store.pk

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("shop:store_products", pk=store_pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'shop/edit_product.html', {
    'product': product,
    'form': form,
    })


def delete_product(request, pk):
    """
    Delete Product
    """
    product = get_object_or_404(Product, pk=pk)
    store_pk = product.store.pk

    if request.method == "POST":
        product.delete()
        messages.success(
            request,
            f"Product {product} deleted successfully."
        )
        return redirect("shop:store_products", pk=store_pk)

    return render(request, "vendor/product_confirm_delete.html", {
        "product": product,
    })


def edit_store(request, pk):
    """
    Edit Store
    """
    store = get_object_or_404(Store, pk=pk, owner=request.user)

    if request.method == "POST":
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect("shop:vendor_dashboard")
    else:
        form = StoreForm(instance=store)

    return render(request, "shop/edit_store.html", {"form": form})


def delete_store(request, pk):
    """
    Delete Store
    """
    store = get_object_or_404(Store, pk=pk, owner=request.user)

    if request.method == "POST":
        store.delete()
        return redirect("shop:vendor_dashboard")

    return render(request, "shop/delete_store.html", {
        "store": store
    })

# ── API ───────────────────────────────────────────────────

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def view_stores(request):
    serializer = StoreSerializer(Store.objects.all(), many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_products(request):
    serializer = ProductSerializer(Product.objects.all(), many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_store(request):
    serializer = StoreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_product(request):
    store_id = request.data.get('store')

    # Ensure the store belongs to the authenticated user
    try:
        store = Store.objects.get(id=store_id, owner=request.user)
    except Store.DoesNotExist:
        return Response(
            {"error": "Store not found or access denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(store=store)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def api_edit_store(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        return Response(
            {'error': 'Store not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = StoreSerializer(store, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def api_delete_store(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        return Response(
            {'error': 'Store not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    store.delete()
    return Response(
        {'message': 'Store deleted successfully'},
        status=status.HTTP_204_NO_CONTENT
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendor_products_with_reviews(request):
    stores = Store.objects.filter(owner=request.user)

    products = Product.objects.filter(
        store__in=stores,
        reviews__isnull=False
    ).distinct()

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendor_reviews(request):
    reviews = Review.objects.filter(
        product__store__owner=request.user
    ).select_related('product', 'user')

    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def vendors_with_stores_and_products(request):
    vendors = User.objects.filter(profile__role='vendor')

    data = []
    for vendor in vendors:
        stores = Store.objects.filter(owner=vendor)
        store_data = []

        for store in stores:
            products = Product.objects.filter(store=store)
            store_data.append({
                "store": store.name,
                "products": ProductSerializer(products, many=True).data
            })

        data.append({
            "vendor": vendor.username,
            "stores": store_data
        })

    return Response(data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request, store_id):
    try:
        store = Store.objects.get(id=store_id, owner=request.user)
    except Store.DoesNotExist:
        return Response(
            {"error": "Store not found or access denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ProductSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(store=store) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_reddit_posts(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
    headers = {
        "User-Agent": "django-course-app/1.0"
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        print(response)
        return []

    try:
        data = response.json()
    except ValueError:
        return []

    posts = []
    for item in data.get("data", {}).get("children", []):
        post = item.get("data", {})
        posts.append({
            "title": post.get("title"),
            "author": post.get("author"),
            "url": "https://www.reddit.com" + post.get("permalink", ""),
        })

    return posts

def reddit_feed(request):
    print("reddit_feed view called")
    posts = get_reddit_posts(10)
    print(posts)
    return render(request, "shop/reddit_feed.html", {"posts": posts})
