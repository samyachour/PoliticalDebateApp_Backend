from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class DebateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debate
        fields = ("pk", "title", "last_updated", "debate_map")

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ("debate", "completed", "seen_points",)

class StarredSerializer(serializers.ModelSerializer):
    class Meta:
        model = Starred
        fields = ("starred_list",)

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

class EmailChangeSerializer(serializers.Serializer):
    """
    Serializer for email change endpoint.
    """
    new_email = serializers.CharField(max_length=255, required=True)
