from django.urls import path
from . import views

urlpatterns = [
    path("reddit/", views.reddit_feed, name="reddit_feed"),
]
