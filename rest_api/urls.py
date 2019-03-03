from django.urls import path
from .views import ListDebatesView, LoginView, DebatesDetailView, ProgressView, RegisterUsers


urlpatterns = [
    path('debates/', ListDebatesView.as_view(), name="debates-all"),
    path('debates/<int:pk>/', DebatesDetailView.as_view(), name="get-debate"),
    path('progress/<int:pk>/', ProgressView.as_view(), name="get-progress"),
    path('progress/', ProgressView.as_view(), name="post-progress"),
    path('auth/login/', LoginView.as_view(), name="auth-login"),
    path('auth/register/', RegisterUsers.as_view(), name="auth-register")
]
