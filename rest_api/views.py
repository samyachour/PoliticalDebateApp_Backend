from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from .models import *
from .serializers import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from .decorators import *
from .helpers.tokens import account_verification_token
from .helpers.email_verification import email_verification
from .helpers.constants import *
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse
from django.contrib.postgres.search import TrigramSimilarity

class SearchDebatesView(generics.ListAPIView):
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        # Just give the user the most recent debates
        if search_string_key not in kwargs:
            debates = self.queryset.order_by('-' + last_updated_key)[:100]
        else:
            search_string = kwargs[search_string_key]
            debates = self.queryset.annotate(
                        similarity=TrigramSimilarity(title_key, search_string),
                      ).filter(similarity__gt=minimum_trigram_similarity).order_by('-' + last_updated_key)[:100]

        serializer = DebateSearchSerializer(instance=debates, many=True)
        return Response(serializer.data)

class DebateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer
    permission_classes = (permissions.AllowAny,)

    @validate_debate_get_request_data
    def get(self, request, *args, **kwargs):
        debate = get_object_or_404(self.queryset, pk=kwargs[pk_key])
        return Response(DebateSerializer(debate).data)

class ProgressView(generics.RetrieveAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @validate_progress_point_get_request_data
    def get(self, request, *args, **kwargs):

        try:
            debate = get_object_or_404(Debate, pk=kwargs[pk_key])
            progress_point = get_object_or_404(self.queryset, user=request.user, debate=debate)
            return Response(ProgressSerializer(progress_point).data)
        except Debate.DoesNotExist:
            return Response(
                data={
                    message_key: "Could not find debate with ID {}".format(kwargs[pk_key])
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class ProgressViewAll(generics.RetrieveAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @validate_progress_post_point_request_data
    def post(self, request, *args, **kwargs):

        try:
            debate = Debate.objects.get(pk=request.data[debate_pk_key])
            progress_point = self.queryset.get(user=request.user, debate=debate)

            existing_seen_points = progress_point.seen_points
            if request.data[debate_point_key] not in existing_seen_points:
                existing_seen_points.append(request.data[debate_point_key])
                # Can't call 'update' on an object (which is what .get() returns)
                self.queryset.filter(user=request.user, debate=debate).update(seen_points=existing_seen_points)

        except Debate.DoesNotExist:
            return Response(
                data={
                    message_key: "Could not find debate with ID {}".format(request.data[debate_pk_key])
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Progress.DoesNotExist:
            progress_point = Progress.objects.create(
                user=request.user,
                debate=debate,
                seen_points=[request.data[debate_point_key]]
            )

        return Response(
            data=ProgressSerializer(progress_point).data,
            status=status.HTTP_201_CREATED
        )

    def get(self, request, *args, **kwargs):

        progress_points = self.queryset.filter(user=request.user)
        return Response(ProgressSerializer(progress_points, many=True).data)

class ProgressCompleted(generics.RetrieveAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @validate_progress_post_completed_request_data
    def post(self, request, *args, **kwargs):

        try:
            debate = Debate.objects.get(pk=request.data[debate_pk_key])
            progress_point = self.queryset.filter(user=request.user, debate=debate)

            if progress_point.count() == 1:
                progress_point.update(completed=request.data[completed_key])
                progress_point = self.queryset.get(user=request.user, debate=debate)
            elif progress_point.count() > 1:
                return Response(
                    data={
                        message_key: "Found duplicate progress point for user ID {} and debate ID {}. This should never happen".format(request.user.pk, request.data[debate_pk_key])
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    data={
                        message_key: "Could not find user progress point with debate ID {}".format(request.data[debate_pk_key])
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Debate.DoesNotExist:
            return Response(
                data={
                    message_key: "Could not find debate with ID {}".format(request.data[debate_pk_key])
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            data=ProgressSerializer(progress_point).data,
            status=status.HTTP_201_CREATED
        )

class StarredView(generics.RetrieveAPIView):
    queryset = Starred.objects.all()
    serializer_class = StarredSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @validate_starred_list_post_request_data
    def post(self, request, *args, **kwargs):

        try:
            newDebate = Debate.objects.get(pk=request.data[debate_pk_key])
            user_starred = self.queryset.get(user=request.user)

            if not user_starred.starred_list.filter(pk=newDebate.pk).exists():
                user_starred.starred_list.add(newDebate)

        except Debate.DoesNotExist:
            return Response(
                data={
                    message_key: "Could not find debate with ID {}".format(request.data[debate_pk_key])
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
                    message_key: "Could not retrieve reading list"
                },
                status=status.HTTP_404_NOT_FOUND
            )

class ChangePasswordView(generics.UpdateAPIView):
    # This permission class will overide the global permission
    # class setting
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()

    @validate_change_password_post_request_data
    def put(self, request, *args, **kwargs):
        self.object = self.request.user

        # Check old password
        if not self.object.check_password(request.data[old_password_key]):
            return Response({old_password_key: ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
        # set_password also hashes the password that the user will get
        self.object.set_password(request.data[new_password_key])
        self.object.save()
        return Response("Success.", status=status.HTTP_200_OK)

class ChangeEmailView(generics.UpdateAPIView):
    # This permission class will overide the global permission
    # class setting
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()

    @validate_change_email_post_request_data
    def put(self, request, *args, **kwargs):
        self.object = self.request.user
        new_email = request.data[new_email_key]

        try:
            # Set username to email, don't set email property until it's verified
            self.object.username = new_email
            email_verification.send_email(self.object, request, new_email)
        # Throws SMTPexception if email fails to send
        except:
            return Response(
                data={
                    message_key: "invalid email"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        self.object.save()
        return Response("Success.", status=status.HTTP_200_OK)

class DeleteUsersView(generics.DestroyAPIView):
    """
    POST auth/delete/
    """
    # This permission class will overide the global permission
    # class setting
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        self.object = self.request.user

        self.object.delete() #Triggers cascading deletions on user data existing on other tables
        return Response("Success.", status=status.HTTP_200_OK)

class RegisterUsersView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    @validate_register_user_post_request_data
    def post(self, request, *args, **kwargs):
        password = request.data[password_key]
        email = request.data[email_key]

        # New user's don't have an email attribute until they verify their email
        new_user = User.objects.create_user(
            username=email, password=password
        )
        try:
            email_verification.send_email(new_user, request, email)
        # Throws SMTPexception if email fails to send
        except:
            new_user.delete()
            return Response(
                data={
                    message_key: "invalid email"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_201_CREATED)

class PasswordResetFormView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'password_reset.html'
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(kwargs[uidb64_key]))
            user = get_object_or_404(User, pk=uid)
        except:
            user = None
        if user is not None and account_verification_token.check_token(user, kwargs[token_key]):
            # User verified email
            user.email = user.username
            user.save()

            return Response({'serializer': PasswordResetFormSerializer(),
                             version_key: v1_key,
                             uidb64_key: kwargs[uidb64_key],
                             token_key: kwargs[token_key],
                             passwords_do_not_match_key: False,
                             password_too_short_key: False
                            })

        else:
            return HttpResponse('Link is invalid!')

class PasswordResetSubmitView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetSubmitSerializer

    def post(self, request, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(kwargs[uidb64_key]))
            user = get_object_or_404(User, pk=uid)
        except:
            user = None
        if user is not None and account_verification_token.check_token(user, kwargs[token_key]):
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                new_password = serializer.data.get(new_password_key)
                new_password_confirmation = serializer.data.get(new_password_confirmation_key)

                user.set_password(new_password)
                user.save()

                return HttpResponse('Password successfully changed!')

            else:
                return HttpResponse('There was a problem. Please try again.')

        else:
            return HttpResponse('Link is invalid!')

class RequestPasswordResetView(generics.RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()

    @validate_request_password_reset_post_request_data
    def post(self, request, *args, **kwargs):
        email = request.data[email_key]

        user = get_object_or_404(User, username=email)
        # We only set the email field after confirming email
        if not user.email and not (force_send_key in request.data and request.data[force_send_key]):
            return Response(
                data={
                    message_key: "user has not verified their email"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            email_verification.send_email(user, request, email, password_reset=True)
        # Throws SMTPexception if email fails to send
        except:
            return Response(
                data={
                    message_key: "invalid email"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response("Success.", status=status.HTTP_200_OK)

class VerificationView(generics.RetrieveAPIView):
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(kwargs[uidb64_key]))
            user = self.queryset.get(pk=uid)
        except:
            user = None
        if user is not None and account_verification_token.check_token(user, kwargs[token_key]):
            # User verified email
            user.email = user.username
            user.save()

            return HttpResponse('Email verified!')

        else:
            return HttpResponse('Activation link is invalid!')
