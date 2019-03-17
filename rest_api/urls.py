from django.urls import path
from .views import *


urlpatterns = [
    path('debates/', ListDebatesView.as_view(), name="debates-all"),
    path('debates/<str:title>', DebatesDetailView.as_view(), name="get-debate"),
    path('progress/<str:debate_title>', ProgressView.as_view(), name="get-progress"),
    path('progress/', ProgressView.as_view(), name="post-progress"),
    path('reading-list/', ReadingListView.as_view(), name="get-reading-list"),
    path('reading-list/', ReadingListView.as_view(), name="post-reading-list"),
    path('auth/login/', LoginView.as_view(), name="auth-login"),
    path('auth/register/', RegisterUsers.as_view(), name="auth-register"),
    path('auth/change-password/', ChangePasswordView.as_view(), name="auth-change-password"),
]
