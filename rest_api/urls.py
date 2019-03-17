from django.urls import path
from .views import *
from rest_framework_jwt.views import refresh_jwt_token

urlpatterns = [
    path('debates/', ListDebatesView.as_view(), name="get-all-debates"),
    path('debate/<int:pk>', DebateDetailView.as_view(), name="get-debate"),
    path('progress/<int:pk>', ProgressView.as_view(), name="get-progress"),
    path('progress/', ProgressViewAll.as_view(), name="get-all-progress"),
    path('progress/', ProgressView.as_view(), name="post-progress"),
    path('progress-completed/', ProgressCompleted.as_view(), name="post-progress-completed"),
    path('starred-list/', StarredView.as_view(), name="get-starred-list"),
    path('starred-list/', StarredView.as_view(), name="post-starred-list"),
    path('auth/login/', LoginView.as_view(), name="auth-login"),
    path('auth/register/', RegisterUsers.as_view(), name="auth-register"),
    path('auth/change-password/', ChangePasswordView.as_view(), name="auth-change-password"),
    path('auth/refresh-token/', refresh_jwt_token, name="auth-refresh-token"),
]
