from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from .utils.constants import *


# DEBATES

# For self referential serializers
class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class PointHyperlinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointHyperlink
        fields = (substring_key, url_key)

class PointSerializer(serializers.ModelSerializer):
    rebuttals = RecursiveField(many=True)
    hyperlinks = PointHyperlinkSerializer(many=True, source='pointhyperlink_set') # one to many

    class Meta:
        model = Point
        fields = (pk_key, short_description_key, description_key, side_key, hyperlinks_key, rebuttals_key)

class DebateSerializer(serializers.ModelSerializer):
    debate_map = PointSerializer(many=True, source='point_set') # one to many

    class Meta:
        model = Debate
        fields = (pk_key, title_key, short_title_key, last_updated_key, debate_map_key)


# PROGRESS

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = (debate_key, seen_points_key,)

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
