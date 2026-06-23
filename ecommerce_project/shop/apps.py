# shop/apps.py
from django.apps import AppConfig


class ShopConfig(AppConfig):
    """
    Application configuration class for the 'shop' app.
    """

    # Specify the default type of primary key field to use for models
    default_auto_field = 'django.db.models.BigAutoField'

    # Name of the Django application
    name = 'shop'