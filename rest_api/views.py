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
from smtplib import SMTPException
from random import shuffle

# DEBATES

class FilterDebatesView(generics.ListCreateAPIView):
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_scope = 'FilterDebates'

    @staticmethod
    def filter_queryset_by_pk_array(array_key, queryset, request, exclusion=False):
        if array_key in request.data:
            pk_array = request.data[array_key]
            if type(pk_array) is not list:
                return debate_filter_invalid_pk_array_format_error
            for pk in pk_array:
                if type(pk) is not int:
                    return debate_filter_invalid_pk_array_items_format_error

            if exclusion:
                return queryset.exclude(pk__in=pk_array)
            else:
                return queryset.filter(pk__in=pk_array)
        else:
            return debate_filter_missing_pk_array_error

    def post(self, request, *args, **kwargs):
        debates = self.queryset # return queryset

        # Handle search string
        if search_string_key in request.data:
            search_string = request.data[search_string_key]

            if search_string and type(search_string) is str:
                debates = debates.annotate(
                            similarity=Greatest(TrigramSimilarity(title_key, search_string),
                                                TrigramSimilarity(tags_key, search_string)),
                          ).filter(similarity__gt=minimum_trigram_similarity)

            else:
                return Response(
                    data={
                        message_key: debate_filter_invalid_search_string_error
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # filter defaults to last updated
        filter = last_updated_filter_value

        # Handle filter input
        if filter_key in request.data:
            filter = request.data[filter_key]
            if type(filter) is not str: # If filter is passed in but in wrong format
                return Response(
                    data={
                        message_key: debate_filter_invalid_filter_format_error
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            # If filter not in list of known filters
            if filter not in all_filters:
                return Response(
                    data={
                        message_key: debate_filter_unknown_filter_error
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        filtered_debates_or_error = None
        if filter == starred_filter_value:
            filtered_debates_or_error = self.filter_queryset_by_pk_array(all_starred_key, debates, request)
        elif filter == progress_filter_value:
            filtered_debates_or_error = self.filter_queryset_by_pk_array(all_progress_key, debates, request)
        elif filter == no_progress_filter_value:
            filtered_debates_or_error = self.filter_queryset_by_pk_array(all_progress_key, debates, request, exclusion=True)
        if type(filtered_debates_or_error) is str: # error message
            return Response(
                data={
                    message_key: filtered_debates_or_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif filtered_debates_or_error is not None:
            debates = filtered_debates_or_error

        # Sort all responses by last updated and truncate array to our maximum
        debates = debates.order_by('-' + last_updated_key)[:maximum_debate_query]

        if filter == random_filter_value:
            debates = list(debates)
            shuffle(debates)

        serializer = DebateFilterSerializer(instance=debates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DebateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_scope = 'DebateDetail'

    @validate_debate_get_request_data
    def get(self, request, *args, **kwargs):
        debate = get_object_or_404(self.queryset, pk=kwargs[pk_key])
        return Response(DebateSerializer(debate).data, status=status.HTTP_200_OK)

# Don't need Create/Read/Update endpoints for debates and points because they should only be interfaced w/ directly from the backend







# PROGRESS

class AllProgressView(generics.RetrieveAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = 'AllProgress'

    @validate_progress_post_point_request_data
    def put(self, request, *args, **kwargs):

        try:
            debate = get_object_or_404(Debate.objects.all(), pk=request.data[debate_pk_key])
            new_point = get_object_or_404(Point.objects.all(), pk=request.data[point_pk_key])
            progress = self.queryset.get(user=request.user, debate=debate)

            progress.seen_points.add(new_point) # add uses a set semantic to prevent duplicates
            progress.completed_percentage = (len(progress.seen_points.all()) / (debate.total_points * 1.0)) * 100
            progress.save()

        except Progress.DoesNotExist:
            progress = Progress.objects.create(
                user=request.user,
                debate=debate,
                completed_percentage= (1 / (debate.total_points * 1.0)) * 100
            )
            progress.seen_points.add(new_point)
            progress.save()

        return Response(success_response, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):

        progress = self.queryset.filter(user=request.user)
        return Response(self.get_serializer(progress, many=True).data, status=status.HTTP_200_OK)

class ProgressBatchView(generics.UpdateAPIView):
    queryset = Progress.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = 'ProgressBatch'

    @validate_progress_post_batch_point_request_data
    def put(self, request, *args, **kwargs):

        for progress_input in request.data[all_debate_points_key]:
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







# STARRED

class StarredView(generics.RetrieveAPIView):
    queryset = Starred.objects.all()
    serializer_class = StarredSerializer
    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = 'Starred'

    @staticmethod
    def starOrUnstarDebates(pk_list, star, starred):
        all_debates = Debate.objects.all()

        for pk_index in range(0, len(pk_list)):
            pk = pk_list[pk_index]
            try:
                newDebate = all_debates.get(pk=pk)

                if star:
                    if not starred.starred_list.filter(pk=newDebate.pk).exists():
                        starred.starred_list.add(newDebate)
                else:
                    if starred.starred_list.filter(pk=newDebate.pk).exists():
                        starred.starred_list.remove(newDebate)
            except Debate.DoesNotExist:
                # Fail silently because it might be a batch post w/ old debates that have since been deleted
                pass

    @validate_starred_post_request_data
    def post(self, request, *args, **kwargs):
        starred_debate_pks = request.data[starred_list_key]
        unstarred_debate_pks = request.data[unstarred_list_key]
        # remove common elements
        starred_debate_pks = list(set(starred_debate_pks)^set(unstarred_debate_pks))

        try:
            starred = self.queryset.get(user=request.user)

        except Starred.DoesNotExist:
            starred = Starred.objects.create(user=request.user)

        self.starOrUnstarDebates(starred_debate_pks, True, starred)
        self.starOrUnstarDebates(unstarred_debate_pks, False, starred)

        return Response(success_response, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        try:
            starred = self.queryset.get(user=request.user)

        except Starred.DoesNotExist:
            starred = Starred.objects.create(user=request.user)

        return Response(StarredSerializer(starred).data, status=status.HTTP_200_OK)







# AUTH

class ChangePasswordView(generics.UpdateAPIView):
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
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    throttle_scope = 'ChangeEmail'

    @validate_change_email_post_request_data
    def put(self, request, *args, **kwargs):
        self.object = self.request.user
        new_email = request.data[new_email_key].lower()
        if new_email == self.object.username:
            return Response(
                data={
                    message_key: already_using_email_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Set username to email, don't set email property until it's verified
            self.object.username = new_email
            self.object.save()
            email_verification.send_email(self.object, request, new_email)
        # Throws SMTPException if email fails to send
        except SMTPException:
            return Response(
                data={
                    message_key: invalid_email_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(success_response, status=status.HTTP_200_OK)

class GetCurrentEmailView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    throttle_scope = 'GetCurrentEmail'

    def get(self, request, *args, **kwargs):
        self.object = self.request.user
        is_verified = len(self.object.email) > 0

        return Response(data={
            current_email_key: self.object.username,
            is_verified_key: is_verified
        }, status=status.HTTP_200_OK)

class RequestVerificationLinkView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    throttle_scope = 'RequestVerificationLink'

    def put(self, request, *args, **kwargs):
        self.object = self.request.user
        email = self.object.username

        try:
            email_verification.send_email(self.object, request, email)
        # Throws SMTPException if email fails to send
        except SMTPException:
            return Response(
                data={
                    message_key: invalid_email_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(success_response, status=status.HTTP_200_OK)

class DeleteUserView(generics.DestroyAPIView):
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
        # Throws SMTPException if email fails to send
        except SMTPException:
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
            # User also verified their email by opening the link (in case they hadn't already)
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
        # Throws SMTPException if email fails to send
        except SMTPException:
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
