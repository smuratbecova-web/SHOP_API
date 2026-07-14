from rest_framework import serializers
from .models import Category, Product, Review
from django.db.models import Avg

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        if len(value) < 3:
            raise serializers.ValidationError("Min length is 3 characters.")
        return value

class CategoryCountSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Product title cannot be empty.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'text', 'stars', 'product']

    def validate_text(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Review text cannot be empty.")
        return value

    def validate_stars(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Stars must be between 1 and 5.")
        return value

class ProductReviewsSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'reviews', 'rating']

    def get_rating(self, obj):
        average = obj.reviews.aggregate(Avg('stars'))['stars__avg']
        if average is None:
            return 0.0
        return round(average, 2)  