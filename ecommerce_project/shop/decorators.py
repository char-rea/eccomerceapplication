"""Custom decorators for role-based access control."""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def vendor_required(view_func):
    """Allow access only to authenticated users with the vendor role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'vendor':
            messages.error(request, 'Access denied. Vendors only.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def buyer_required(view_func):
    """Allow access only to authenticated users with the buyer role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'buyer':
            messages.error(request, 'Access denied. Buyers only.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper