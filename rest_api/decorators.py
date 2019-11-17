from rest_framework.response import Response
from rest_framework.views import status
from .utils.constants import *

# DEBATES

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


# PROGRESS

def validate_progress_post_point_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        debate = args[0].request.data.get(debate_pk_key, "")
        point = args[0].request.data.get(point_pk_key, "")
        if not debate or not point:
            return Response(
                data={
                    message_key: progress_point_post_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_progress_batch_post_point_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        all_debate_points = args[0].request.data.get(all_debate_points_key, "")
        if not all_debate_points:
            return Response(
                data={
                    message_key: progress_point_batch_post_key_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if type(all_debate_points) is not list:
            return Response(
                data={
                    message_key: progress_point_batch_post_data_format_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        for progress_input in all_debate_points:
            if debate_key not in progress_input:
                return Response(
                    data={
                        message_key: progress_point_batch_post_debate_key_error
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            if seen_points_key not in progress_input:
                return Response(
                    data={
                        message_key: progress_point_batch_post_seen_points_key_error
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            if type(progress_input[seen_points_key]) is not list:
                return Response(
                    data={
                        message_key: progress_point_batch_post_data_format_error
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        return fn(*args, **kwargs)
    return decorated


# STARRED

def validate_starred_post_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        starred_debate_pks = args[0].request.data.get(starred_list_key, "")
        unstarred_debate_pks = args[0].request.data.get(unstarred_list_key, "")
        if (type(starred_debate_pks) is not list) or (type(unstarred_debate_pks) is not list):
            return Response(
                data={
                    message_key: starred_post_type_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if (not starred_debate_pks) and (not unstarred_debate_pks):
            return Response(
                data={
                    message_key: starred_post_empty_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        for pk in starred_debate_pks + unstarred_debate_pks:
            if type(pk) is not int:
                return Response(
                    data={
                        message_key: starred_post_format_error
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        return fn(*args, **kwargs)
    return decorated


# AUTH

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
