from rest_framework.response import Response
from rest_framework.views import status

def validate_debate_get_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        title =  kwargs["pk"]
        if not title:
            return Response(
                data={
                    "message": "A debate ID is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_progress_point_get_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        title = kwargs["pk"]
        if not title:
            return Response(
                data={
                    "message": "A debate ID is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_progress_post_point_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        debate_title = args[0].request.data.get("debate_pk", "")
        debate_point = args[0].request.data.get("debate_point", "")
        if not debate_title and not debate_point:
            return Response(
                data={
                    "message": "Both debate ID and debate point are required to add a progress point"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_progress_post_completed_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        debate_title = args[0].request.data.get("debate_pk", "")
        debate_point = args[0].request.data.get("completed", "")
        if not debate_title and not debate_point:
            return Response(
                data={
                    "message": "Both debate ID and completed status are required to update completed status"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_starred_list_post_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        debate_title = args[0].request.data.get("debate_pk", "")
        if not debate_title:
            return Response(
                data={
                    "message": "A debate ID is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated
