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
                    message_key: debate_get_error
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
                    message_key: progress_point_get_error
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
                    message_key: progress_point_post_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_starred_post_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        starred_debate_ids = args[0].request.data.get(starred_list_key, "")
        unstarred_debate_ids = args[0].request.data.get(unstarred_list_key, "")
        if not (starred_debate_ids or unstarred_debate_ids) or
        type(starred_debate_ids) is not list or type(unstarred_debate_ids) is not list
        or (len(starred_debate_ids) + len(unstarred_debate_ids) == 0)
        or (len(starred_debate_ids) > 0 && type(starred_debate_ids[0]) is not int
        or (len(unstarred_debate_ids) > 0 && type(unstarred_debate_ids[0]) is not int:
            return Response(
                data={
                    message_key: starred_post_error
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
                    message_key: register_post_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(password) < minimum_password_length:
            return Response(
                data={
                    message_key: password_length_error
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
                    message_key: change_password_post_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(new_password) < minimum_password_length:
            return Response(
                data={
                    message_key: password_length_error
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
                    message_key: change_email_post_error
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
                    message_key: request_password_reset_post_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated
