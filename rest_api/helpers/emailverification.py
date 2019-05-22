from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode
from .tokens import account_verification_token
from django.core.mail import send_mail

class EmailVerification():
    # Send an email to the user with the token:
    def send_email(self, user, request, email, password_reset=False):
        # Encode user ID
        uid = force_text(urlsafe_base64_encode(force_bytes(user.pk)))
        token = account_verification_token.make_token(user)

        # Remove old auth parameters
        verification_link_arr = request.build_absolute_uri().split("/")
        verification_link_arr = verification_link_arr[ : verification_link_arr.index("auth") + 1]

        # Append our activation parameters
        verification_link = "/".join(verification_link_arr) + "/verify/{1}/{2}/{3}".format(get_current_site(request), uid, token, 1 if password_reset else 0)

        send_mail(
            'Verify your PoliticalDebateApp account email.',
            "Please click the following link to verify your email address:\n\n {0}".format(verification_link),
            'admin@politicaldebateapp.com',
            [email],
            fail_silently=False,
        )

email_verification = EmailVerification()
