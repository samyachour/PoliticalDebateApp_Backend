from django.urls import path
from .views import ListDebatesView


urlpatterns = [
    path('debates/', ListDebatesView.as_view(), name="debates-all")
]
