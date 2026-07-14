from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
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


class CategoryListAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.annotate(products_count=Count('products'))
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CategorySerializer
        return CategoryCountSerializer


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'



class ProductListAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'


class ProductReviewsListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductReviewsSerializer



class ReviewListAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    lookup_field = 'id'




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