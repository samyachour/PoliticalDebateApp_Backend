from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from .helpers.constants import *

# DEBATES

class DebateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debate
        fields = (pk_key, title_key, last_updated_key, total_points_key, debate_map_key)

class DebateSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debate
        fields = (pk_key, title_key, last_updated_key, total_points_key)

# PROGRESS

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = (debate_key, completed_key, seen_points_key,)

# STARRED

class StarredSerializer(serializers.ModelSerializer):
    class Meta:
        model = Starred
        fields = (starred_list_key,)

# AUTH

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (username_key, email_key)

class PasswordResetFormSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        max_length=100,
        style={'input_type': 'password', 'placeholder': 'New password'}
    )
    new_password_confirmation = serializers.CharField(
        max_length=100,
        style={'input_type': 'password', 'placeholder': 'New password'}
    )

class PasswordResetSubmitSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=255, required=True)
    new_password_confirmation = serializers.CharField(max_length=255, required=True)
