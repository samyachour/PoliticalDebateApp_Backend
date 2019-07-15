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
from django.db.models.functions import Greatest
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# DEBATES

class SearchDebatesView(generics.ListAPIView):
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_scope = 'SearchDebates'

    def get(self, request, *args, **kwargs):
        # Just give the user the most recent debates
        if search_string_key not in kwargs:
            debates = self.queryset.order_by('-' + last_updated_key)[:maximum_debate_query]
        else:
            search_string = kwargs[search_string_key]
            debates = self.queryset.annotate(
                        similarity=Greatest(TrigramSimilarity(title_key, search_string),
                                            TrigramSimilarity(tags_key, search_string)),
                      ).filter(similarity__gt=minimum_trigram_similarity).order_by('-' + last_updated_key)[:maximum_debate_query]

        serializer = DebateSearchSerializer(instance=debates, many=True)
        return Response(serializer.data)

class DebateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_scope = 'DebateDetail'

    @validate_debate_get_request_data
    def get(self, request, *args, **kwargs):
        debate = get_object_or_404(self.queryset, pk=kwargs[pk_key])
        return Response(DebateSerializer(debate).data)

# Don't need CUD endpoints for debates and points because they should only be interfaced w/ directly







# PROGRESS

class ProgressDetailView(generics.RetrieveAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = 'ProgressDetail'

    @validate_progress_point_get_request_data
    def get(self, request, *args, **kwargs):
        debate = get_object_or_404(Debate, pk=kwargs[pk_key])
        progress_point = get_object_or_404(self.queryset, user=request.user, debate=debate)
        return Response(ProgressSerializer(progress_point).data)

class AllProgressView(generics.RetrieveAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = 'AllProgress'

    @validate_progress_post_point_request_data
    def post(self, request, *args, **kwargs):

        try:
            debate = get_object_or_404(Debate.objects.all(), pk=request.data[debate_pk_key])
            new_point = get_object_or_404(Point.objects.all(), pk=request.data[point_pk_key])
            progress = self.queryset.get(user=request.user, debate=debate)

            progress.seen_points.add(new_point) # add uses a set semantic to prevent duplicates
            progress.completed_percentage = (len(progress.seen_points.all()) / (debate.total_points * 1.0)) * 100
            progress.save()

        except Progress.DoesNotExist:
            progress_points = Progress.objects.create(
                user=request.user,
                debate=debate,
                completed_percentage= (1 / (debate.total_points * 1.0)) * 100
            )
            progress_points.seen_points.add(new_point)

        return Response(success_response, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):

        progress = self.queryset.filter(user=request.user)
        return Response(ProgressAllSerializer(progress, many=True).data)

class ProgressBatchView(generics.UpdateAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressBatchInputSerializer
    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = 'ProgressBatch'

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            for progress_input in serializer.data[all_debate_points_key]:
                try:
                    debate = Debate.objects.all().get(pk=progress_input[debate_key])
                    new_points = progress_input[seen_points_key]
                    progress = self.queryset.get(user=request.user, debate=debate)

                except Debate.DoesNotExist:
                    # Fail silently in finding the debate object because we could receive a batch request with an old debate that has since been deleted
                    pass

                except Progress.DoesNotExist:
                    progress = Progress.objects.create(
                        user=request.user,
                        debate=debate,
                        completed_percentage=(len(progress_input[seen_points_key]) / (debate.total_points * 1.0)) * 100
                    )

                all_points = Point.objects.all()
                for new_point_pk in new_points:
                    try:
                        new_point = all_points.get(pk=new_point_pk)
                        progress.seen_points.add(new_point) # add uses a set semantic to prevent duplicates
                    except Point.DoesNotExist:
                        # Fail silently in finding the new point object because we could receive a batch request with old debate points that have since been deleted
                        pass

                progress.completed_percentage = (len(progress.seen_points.all()) / (debate.total_points * 1.0)) * 100
                progress.save()

            return Response(success_response, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={
                    message_key: progress_point_batch_post_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )







# STARRED

class StarredView(generics.RetrieveAPIView):
    queryset = Starred.objects.all()
    serializer_class = StarredSerializer
    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = 'Starred'

    @validate_starred_post_request_data
    def post(self, request, *args, **kwargs):
        starred_debate_pks = request.data[starred_list_key]
        unstarred_debate_pks = request.data[unstarred_list_key]

        try:
            starred = self.queryset.get(user=request.user)

            for pk_index in range(0, len(unstarred_debate_pks)):
                pk = unstarred_debate_pks[pk_index]
                newDebate = get_object_or_404(Debate.objects.all(), pk=pk)

                if starred.starred_list.filter(pk=newDebate.pk).exists():
                    starred.starred_list.remove(newDebate)

            for pk_index in range(0, len(starred_debate_pks)):
                pk = starred_debate_pks[pk_index]
                newDebate = get_object_or_404(Debate.objects.all(), pk=pk)

                if not starred.starred_list.filter(pk=newDebate.pk).exists():
                    starred.starred_list.add(newDebate)

        except Starred.DoesNotExist:
            starred = Starred.objects.create(user=user)
            for pk_index in range(0, len(starred_debate_pks)):
                pk = starred_debate_pks[pk_index]
                if pk not in unstarred_debate_pks:
                    newDebate = get_object_or_404(Debate.objects.all(), pk=pk)
                    starred.starred_list.add(newDebate)

        return Response(success_response, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):

        starred = get_object_or_404(self.queryset, user=request.user)
        return Response(StarredSerializer(starred).data)







# AUTH

class ChangePasswordView(generics.UpdateAPIView):
    # This permission class will overide the global permission
    # class setting
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    throttle_scope = 'ChangePassword'

    @validate_change_password_post_request_data
    def put(self, request, *args, **kwargs):
        self.object = self.request.user

        # Check old password
        if not self.object.check_password(request.data[old_password_key]):
            return Response({old_password_key: ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
        # set_password also hashes the password that the user will get
        self.object.set_password(request.data[new_password_key])
        self.object.save()
        return Response(success_response, status=status.HTTP_200_OK)

class ChangeEmailView(generics.UpdateAPIView):
    # This permission class will overide the global permission
    # class setting
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    throttle_scope = 'ChangeEmail'

    @validate_change_email_post_request_data
    def put(self, request, *args, **kwargs):
        self.object = self.request.user
        new_email = request.data[new_email_key].lower()

        try:
            # Set username to email, don't set email property until it's verified
            self.object.username = new_email
            email_verification.send_email(self.object, request, new_email)
        # Throws SMTPexception if email fails to send
        except:
            return Response(
                data={
                    message_key: invalid_email_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        self.object.save()
        return Response(success_response, status=status.HTTP_200_OK)

class DeleteUserView(generics.DestroyAPIView):
    """
    POST auth/delete/
    """
    # This permission class will overide the global permission
    # class setting
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    throttle_scope = 'DeleteUser'

    def post(self, request, *args, **kwargs):
        self.object = self.request.user

        self.object.delete() # Triggers cascading deletions on user data existing on other tables
        return Response(success_response, status=status.HTTP_200_OK)

class RegisterUserView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    throttle_scope = 'RegisterUser'

    @validate_register_user_post_request_data
    def post(self, request, *args, **kwargs):
        password = request.data[password_key]
        email = request.data[email_key].lower()

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
                    message_key: invalid_email_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(success_response, status=status.HTTP_201_CREATED)

class PasswordResetFormView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'password_reset.html'
    queryset = User.objects.all()
    throttle_scope = 'PasswordResetForm'

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
            return HttpResponse(invalid_link_error)

class PasswordResetSubmitView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetSubmitSerializer
    throttle_scope = 'PasswordResetSubmit'

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

                user.set_password(new_password)
                user.save()

                return HttpResponse('Password successfully changed!')

            else:
                return HttpResponse('There was a problem, please try again.')

        else:
            return HttpResponse(invalid_link_error)

class RequestPasswordResetView(generics.RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    throttle_scope = 'RequestPasswordReset'

    @validate_request_password_reset_post_request_data
    def post(self, request, *args, **kwargs):
        email = request.data[email_key].lower()

        user = get_object_or_404(User, username=email)
        # We only set the email field after confirming email
        if not user.email and not (force_send_key in request.data and request.data[force_send_key]):
            return Response(
                data={
                    message_key: "Please verify your email."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            email_verification.send_email(user, request, email, password_reset=True)
        # Throws SMTPexception if email fails to send
        except:
            return Response(
                data={
                    message_key: invalid_email_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(success_response, status=status.HTTP_200_OK)

class VerificationView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    throttle_scope = 'Verification'

    def get(self, request, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(kwargs[uidb64_key]))
            user = self.queryset.get(pk=uid)

            if account_verification_token.check_token(user, kwargs[token_key]):
                # User verified email
                user.email = user.username
                user.save()

                return HttpResponse('Email verified!')

            else:
                return HttpResponse(invalid_link_error)
        except:
            return HttpResponse(invalid_link_error)

# Need to override to give throttle scopes
class CustomTokenObtainPairView(TokenObtainPairView):
    throttle_scope = 'TokenObtainPair'

class CustomTokenRefreshView(TokenRefreshView):
    throttle_scope = 'TokenRefresh'
