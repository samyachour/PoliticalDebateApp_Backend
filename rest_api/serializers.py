from rest_framework import serializers
from .models import Debates, Progress
from django.contrib.auth.models import User


class DebatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debates
        fields = ("title", "subtitle")

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ("debate_title", "debate_point")

class TokenSerializer(serializers.Serializer):
    """
    This serializer serializes the token data
    """
    token = serializers.CharField(max_length=255)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email")
