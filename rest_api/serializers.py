from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from .helpers.constants import *

class DebateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debate
        fields = (pk_key, title_key, last_updated_key, debate_map_key)

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = (debate_key, completed_key, seen_points_key,)

class StarredSerializer(serializers.ModelSerializer):
    class Meta:
        model = Starred
        fields = (starred_list_key,)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (username_key, email_key)

# For generating HTML form
class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        max_length=100,
        style={'input_type': 'password', 'placeholder': 'New password'}
    )
    new_password_confirmation = serializers.CharField(
        max_length=100,
        style={'input_type': 'password', 'placeholder': 'New password'}
    )
