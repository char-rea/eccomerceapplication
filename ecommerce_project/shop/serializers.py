from rest_framework import serializers
from .models import Store, Product, Review

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "rating", "comment", "verified", "created", "user"]


class ProductSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "store", "name", "slug",
            "description", "price", "available",
            "reviews"
        ]
        read_only_fields = ["slug"]