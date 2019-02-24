from django.shortcuts import render
from rest_framework import generics
from .models import Debates
from .serializers import DebatesSerializer


class ListDebatesView(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    queryset = Debates.objects.all()
    serializer_class = DebatesSerializer
