from django.shortcuts import render
from rest_framework import generics
from .models import Debates, Progress
from .serializers import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework_jwt.settings import api_settings
from rest_framework import permissions, status
from rest_framework.response import Response
from .decorators import validate_progress_point_request_data

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

class ListDebatesView(generics.ListAPIView):
    """
    GET debates/
    """
    queryset = Debates.objects.all()
    serializer_class = DebatesSerializer
    permission_classes = (permissions.AllowAny,)


class DebatesDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET debates/:id/
    """
    queryset = Debates.objects.all()
    serializer_class = DebatesSerializer
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            debate = self.queryset.get(pk=kwargs["pk"])
            return Response(DebatesSerializer(debate).data)
        except Debates.DoesNotExist:
            return Response(
                data={
                    "message": "Debate with id: {} does not exist".format(kwargs["pk"])
                },
                status=status.HTTP_404_NOT_FOUND
            )

class ProgressView(generics.RetrieveAPIView):
    """
    GET progress/:id/
    POST progress/
    """
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @validate_progress_point_request_data
    def post(self, request, *args, **kwargs):

        try:
            progress_point = self.queryset.get(user=request.user, debate_title = request.data["debate_title"])

            existing_seen_points = progress_point.seen_points
            if request.data['debate_point'] not in existing_seen_points:
                existing_seen_points.append(request.data['debate_point'])

            progress_point.update(seen_points=existing_seen_points)

        except Progress.DoesNotExist:
            progress_point = Progress.objects.create(
                user=request.user,
                debate_title=request.data["debate_title"],
                seen_points=[request.data["debate_point"]]
            )

        return Response(
            data=ProgressSerializer(progress_point).data,
            status=status.HTTP_201_CREATED
        )

    def get(self, request, *args, **kwargs):

        try:
            progress_point = self.queryset.get(pk=kwargs["pk"])
            return Response(ProgressSerializer(progress_point).data)
        except Progress.DoesNotExist:
            return Response(
                data={
                    "message": "Could not retrieve progress"
                },
                status=status.HTTP_404_NOT_FOUND
            )

class LoginView(generics.CreateAPIView):
    """
    POST auth/login/
    """
    # This permission class will overide the global permission
    # class setting
    permission_classes = (permissions.AllowAny,)

    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # login saves the user’s ID in the session,
            # using Django’s session framework.
            login(request, user)
            serializer = TokenSerializer(data={
                # using drf jwt utility functions to generate a token
                "token": jwt_encode_handler(
                    jwt_payload_handler(user)
                )})
            serializer.is_valid()
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

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
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        email = request.data.get("email", "")
        if not username and not password and not email:
            return Response(
                data={
                    "message": "username, password and email is required to register a user"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        new_user = User.objects.create_user(
            username=username, password=password, email=email
        )
        return Response(status=status.HTTP_201_CREATED)
