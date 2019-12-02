from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode
from .token_generator import account_verification_token
from django.core.mail import send_mail
from .constants import *
from django.conf import settings

class EmailVerification():
    # Send an email to the user with the token:
    def send_email(self, user, request, email, password_reset=False):
        # Encode user ID
        uid = force_text(urlsafe_base64_encode(force_bytes(user.pk)))
        token = account_verification_token.make_token(user)

        # Remove old auth parameters
        verification_link_arr = request.build_absolute_uri().split("/")
        verification_link_arr = verification_link_arr[ : verification_link_arr.index(auth_string) + 1]

        if password_reset:
            verification_link = "/".join(verification_link_arr) + "/{0}/{1}/{2}".format(password_reset_form_string, uid, token)

            send_mail(
                'Reset your PoliticalDebateApp password.',
                "Please click the following link to reset your password:\n\n {0}".format(verification_link),
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

        else:
            verification_link = "/".join(verification_link_arr) + "/{0}/{1}/{2}".format(verify_string, uid, token)

            send_mail(
                'Verify your PoliticalDebateApp account email.',
                "Please click the following link to verify your email address:\n\n {0}".format(verification_link),
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

email_verification = EmailVerification()
