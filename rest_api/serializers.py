from rest_framework import serializers
from .models import Debates


class DebatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debates
        fields = ("title", "subtitle")
