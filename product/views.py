from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count

from .models import Category, Product, Review, UserConfirmation
from .serializers import (
    CategorySerializer, CategoryCountSerializer, 
    ProductSerializer, ProductReviewsSerializer, ReviewSerializer,
    UserRegisterSerializer, UserLoginSerializer, UserConfirmSerializer
)


class CategoryListAPIView(APIView):
    def get(self, request):
        categories = Category.objects.annotate(products_count=Count('products'))
        serializer = CategoryCountSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailAPIView(APIView):
    def get(self, request, id):
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductListAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductReviewsListAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductReviewsSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewListAPIView(APIView):
    def get(self, request):
        reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailAPIView(APIView):
    def get(self, request, id):
        try:
            review = Review.objects.get(id=id)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        try:
            review = Review.objects.get(id=id)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            review = Review.objects.get(id=id)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)
        
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "User created. Check console for confirmation code."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user is not None:
                if not user.is_active:
                    return Response({"error": "User is not active. Please confirm your account."}, status=status.HTTP_403_FORBIDDEN)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmAPIView(APIView):
    def post(self, request):
        serializer = UserConfirmSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            code = serializer.validated_data['code']
            try:
                user = User.objects.get(username=username)
                confirmation = UserConfirmation.objects.get(user=user, code=code)
                user.is_active = True
                user.save()
                confirmation.delete()
                return Response({"status": "User successfully confirmed and activated."}, status=status.HTTP_200_OK)
            except (User.DoesNotExist, UserConfirmation.DoesNotExist):
                return Response({"error": "Invalid username or confirmation code."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)