from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class DebatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debates
        fields = ("title", "subtitle")

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ("debate", "seen_points")

class TokenSerializer(serializers.Serializer):
    """
    This serializer serializes the token data
    """
    token = serializers.CharField(max_length=255)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email")

class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(max_length=255, required=True)
    new_password = serializers.CharField(max_length=255, required=True)
