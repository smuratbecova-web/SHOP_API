from rest_framework import serializers
from .models import Category, Product, Review
from django.db.models import Avg  

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

# Для вывода категорий с количеством товаров
class CategoryCountSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)  

    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'text', 'stars', 'product']  


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