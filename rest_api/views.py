from django.shortcuts import render
from rest_framework import generics
from .models import *
from .serializers import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework import permissions, status
from rest_framework.response import Response
from .decorators import *

class ListDebatesView(generics.ListAPIView):
    """
    GET debates/
    """
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer
    permission_classes = (permissions.AllowAny,)

class DebateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET debate/<int:pk>
    """
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer
    permission_classes = (permissions.AllowAny,)

    @validate_debate_get_request_data
    def get(self, request, *args, **kwargs):
        try:
            debate = self.queryset.get(pk=kwargs["pk"])
            return Response(DebateSerializer(debate).data)
        except Debate.DoesNotExist:
            return Response(
                data={
                    "message": "Debate with ID: {} does not exist".format(kwargs["pk"])
                },
                status=status.HTTP_404_NOT_FOUND
            )

class ProgressView(generics.RetrieveAPIView):
    """
    GET progress/<int:pk>
    """
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @validate_progress_point_get_request_data
    def get(self, request, *args, **kwargs):

        try:
            debate = Debate.objects.get(pk=kwargs["pk"])
            progress_point = self.queryset.get(user=request.user, debate=debate)
            return Response(ProgressSerializer(progress_point).data)
        except Debate.DoesNotExist:
            return Response(
                data={
                    "message": "Could not find debate with ID {}".format(kwargs["pk"])
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Progress.DoesNotExist:
            return Response(
                data={
                    "message": "Could not retrieve progress"
                },
                status=status.HTTP_404_NOT_FOUND
            )

class ProgressViewAll(generics.RetrieveAPIView):
    """
    GET progress/
    POST progress/
    """
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @validate_progress_post_point_request_data
    def post(self, request, *args, **kwargs):

        try:
            debate = Debate.objects.get(pk=request.data["debate_pk"])
            progress_point = self.queryset.get(user=request.user, debate=debate)

            existing_seen_points = progress_point.seen_points
            if request.data['debate_point'] not in existing_seen_points:
                existing_seen_points.append(request.data['debate_point'])
                # Can't call 'update' on an object (which is what .get() returns)
                self.queryset.filter(user=request.user, debate=debate).update(seen_points=existing_seen_points)

        except Debate.DoesNotExist:
            return Response(
                data={
                    "message": "Could not find debate with ID {}".format(request.data["debate_pk"])
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Progress.DoesNotExist:
            progress_point = Progress.objects.create(
                user=request.user,
                debate=debate,
                seen_points=[request.data["debate_point"]]
            )

        return Response(
            data=ProgressSerializer(progress_point).data,
            status=status.HTTP_201_CREATED
        )

    def get(self, request, *args, **kwargs):

        progress_points = self.queryset.filter(user=request.user)
        print(progress_points)
        return Response(ProgressSerializer(progress_points, many=True).data)

class ProgressCompleted(generics.RetrieveAPIView):
    """
    POST progress-completed/
    """
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @validate_progress_post_completed_request_data
    def post(self, request, *args, **kwargs):

        try:
            debate = Debate.objects.get(pk=request.data["debate_pk"])
            progress_point = self.queryset.filter(user=request.user, debate=debate)

            if progress_point.count() == 1:
                progress_point.update(completed=request.data["completed"])
                progress_point = self.queryset.get(user=request.user, debate=debate)
            elif progress_point.count() > 1:
                return Response(
                    data={
                        "message": "Found duplicate progress point for user ID {} and debate ID {}. This should never happen".format(request.user.pk, request.data["debate_pk"])
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    data={
                        "message": "Could not find user progress point with debate ID {}".format(request.data["debate_pk"])
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Debate.DoesNotExist:
            return Response(
                data={
                    "message": "Could not find debate with ID {}".format(request.data["debate_pk"])
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            data=ProgressSerializer(progress_point).data,
            status=status.HTTP_201_CREATED
        )

class StarredView(generics.RetrieveAPIView):
    """
    GET starred-list/
    POST starred-list/
    """
    queryset = Starred.objects.all()
    serializer_class = StarredSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @validate_starred_list_post_request_data
    def post(self, request, *args, **kwargs):

        try:
            newDebate = Debate.objects.get(pk=request.data["debate_pk"])
            user_starred = self.queryset.get(user=request.user)

            if not user_starred.starred_list.filter(pk=newDebate.pk).exists():
                user_starred.starred_list.add(newDebate)

        except Debate.DoesNotExist:
            return Response(
                data={
                    "message": "Could not find debate with ID {}".format(request.data["debate_pk"])
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Starred.DoesNotExist:
            user_starred = Starred.objects.create(
                user=request.user
            )
            user_starred.starred_list.add(newDebate)


        return Response(
            data=StarredSerializer(user_starred).data,
            status=status.HTTP_201_CREATED
        )

    def get(self, request, *args, **kwargs):

        try:
            starred = self.queryset.get(user=request.user)
            return Response(StarredSerializer(starred).data)
        except Starred.DoesNotExist:
            return Response(
                data={
                    "message": "Could not retrieve reading list"
                },
                status=status.HTTP_404_NOT_FOUND
            )

class ChangePasswordView(generics.CreateAPIView):
    """
    POST auth/change-password/
    """
    # This permission class will overide the global permission
    # class setting
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PasswordChangeSerializer
    queryset = User.objects.all()

    def put(self, request, *args, **kwargs):
        self.object = self.request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response("Success.", status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterUsers(generics.CreateAPIView):
    """
    POST auth/register/
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        password = request.data.get("password", "")
        email = request.data.get("email", "")
        if not email or not password:
            return Response(
                data={
                    "message": "a username, password and email are required to register a user"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        new_user = User.objects.create_user(
            username=email, password=password, email=email
        )
        return Response(status=status.HTTP_201_CREATED)
