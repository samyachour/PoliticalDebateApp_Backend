from rest_framework.response import Response
from rest_framework.views import status
from .helpers.constants import *

def validate_debate_get_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        title =  kwargs[pk_key]
        if not title:
            return Response(
                data={
                    message_key: "A debate ID is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_progress_point_get_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        title = kwargs[pk_key]
        if not title:
            return Response(
                data={
                    message_key: "A debate ID is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_progress_post_point_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        debate_title = args[0].request.data.get(pk_key, "")
        debate_point = args[0].request.data.get(debate_point_key, "")
        if not debate_title or not debate_point:
            return Response(
                data={
                    message_key: "Both debate ID and debate point are required to add a progress point"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_starred_list_post_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        debate_title = args[0].request.data.get(pk_key, "")
        if not debate_title:
            return Response(
                data={
                    message_key: "A debate ID is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_register_user_post_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        email = args[0].request.data.get(email_key, "")
        password = args[0].request.data.get(password_key, "")
        if not email or not password:
            return Response(
                data={
                    message_key: "Both an email and a password are required to register a user"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(password) < minimum_password_length:
            return Response(
                data={
                    message_key: "Password must be at least 6 characters"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_change_password_post_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        old_password = args[0].request.data.get(old_password_key, "")
        new_password = args[0].request.data.get(new_password_key, "")
        if not old_password or not new_password:
            return Response(
                data={
                    message_key: "Both the old and new password are required to change user's password"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(new_password) < minimum_password_length:
            return Response(
                data={
                    message_key: "New password must be at least 6 characters"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_change_email_post_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        new_email = args[0].request.data.get(new_email_key, "")
        if not new_email:
            return Response(
                data={
                    message_key: "A new email is required to change the user's email"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_request_password_reset_post_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        email = args[0].request.data.get(email_key, "")
        if not email:
            return Response(
                data={
                    message_key: "Need an email to request a password reset"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated
