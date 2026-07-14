import random
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import Category, Product, Review, UserConfirmation

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

class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Username cannot be empty.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )
        code = str(random.randint(100000, 999999))
        UserConfirmation.objects.create(user=user, code=code)
        print(f"\n[DEBUG] Confirmation code for {user.username} is: {code}\n")
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserConfirmSerializer(serializers.Serializer):
    username = serializers.CharField()
    code = serializers.CharField(max_length=6, min_length=6)

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Code must contain only digits.")
        return value