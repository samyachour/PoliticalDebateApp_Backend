from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('debates/', ListDebatesView.as_view(), name="get-all-debates"),
    path('debate/<int:pk>', DebateDetailView.as_view(), name="get-debate"),
    path('progress/<int:pk>', ProgressView.as_view(), name="get-progress"),
    path('progress/', ProgressViewAll.as_view(), name="get-all-progress"),
    path('progress/', ProgressView.as_view(), name="post-progress"),
    path('progress-completed/', ProgressCompleted.as_view(), name="post-progress-completed"),
    path('starred-list/', StarredView.as_view(), name="get-starred-list"),
    path('starred-list/', StarredView.as_view(), name="post-starred-list"),
    path('auth/register/', RegisterUsersView.as_view(), name="auth-register"),
    path('auth/change-password/', ChangePasswordView.as_view(), name="auth-change-password"),
    path('auth/change-email/', ChangeEmailView.as_view(), name="auth-change-email"),
    path('auth/token/obtain/', TokenObtainPairView.as_view(), name='auth-token-obtain'), # Login
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('auth/verify/<str:uidb64>/<str:token>/<int:password_reset>', VerificationView.as_view(), name='auth-verify'),
]
