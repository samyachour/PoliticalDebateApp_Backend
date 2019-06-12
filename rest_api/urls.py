from django.urls import path
from .views import *
from .helpers.constants import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [

    # DEBATES

    path('debate/search/'.format(search_string_key), SearchDebatesView.as_view(), name=search_debates_name),
    path('debate/search/<str:{0}>'.format(search_string_key), SearchDebatesView.as_view(), name=search_debates_name),
    path('debate/<int:{0}>'.format(pk_key), DebateDetailView.as_view(), name=get_debate_name),


    # PROGRESS

    path('progress/<int:{0}>'.format(pk_key), ProgressDetailView.as_view(), name=get_progress_name),
    path('progress/', AllProgressView.as_view(), name=get_all_post_progress_name),
    path('progress/batch/', ProgressBatchView.as_view(), name=post_progress_batch_name),


    # STARRED

    path('starred/', StarredView.as_view(), name=starred_name),


    # AUTH

    path('{0}/delete/'.format(auth_string), DeleteUserView.as_view(), name=auth_delete_name),
    path('{0}/register/'.format(auth_string), RegisterUserView.as_view(), name=auth_register_name),
    path('{0}/change-password/'.format(auth_string), ChangePasswordView.as_view(), name=auth_change_password_name),
    path('{0}/change-email/'.format(auth_string), ChangeEmailView.as_view(), name=auth_change_email_name),
    path('{0}/token/obtain/'.format(auth_string), TokenObtainPairView.as_view(), name=auth_token_obtain_name), # Login
    path('{0}/token/refresh/'.format(auth_string), TokenRefreshView.as_view(), name=auth_token_refresh_name),
    path('{0}/{1}/<str:{2}>/<str:{3}>'.format(auth_string, password_reset_form_string, uidb64_key, token_key), PasswordResetFormView.as_view(), name=auth_password_reset_form_name),
    path('{0}/{1}/<str:{2}>/<str:{3}>/'.format(auth_string, password_reset_submit_string, uidb64_key, token_key), PasswordResetSubmitView.as_view(), name=auth_password_reset_submit_name),
    path('{0}/request-password-reset/'.format(auth_string), RequestPasswordResetView.as_view(), name=auth_request_password_reset_name),
    path('{0}/{1}/<str:{2}>/<str:{3}>'.format(auth_string, verify_string, uidb64_key, token_key), VerificationView.as_view(), name=auth_verify_name),
]
