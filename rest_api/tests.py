from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient, APIRequestFactory, force_authenticate
from rest_framework.views import status
from rest_api.models import *
from .serializers import *
import json
from datetime import datetime
from .views import *
from .helpers.constants import *

# tests for views

class BaseViewTest(APITestCase):
    client = APIClient()

    # DEBATES

    def filter_debates(self, data):
        url = reverse(
            filter_debates_name,
            kwargs={
                version_key: v1_key
            },
        )
        return self.client.post(url,
                                data=json.dumps(data),
                                content_type=content_type)

    def fetch_a_debate(self, pk):
        url = reverse(
            get_debate_name,
            kwargs={
                version_key: v1_key,
                pk_key: pk
            },
        )
        return self.client.get(url)








    # PROGRESS

    @staticmethod
    def create_progress_point(user, debate, point):
        progress = Progress.objects.create(user=user, debate=debate, completed_percentage=(1 / (debate.total_points * 1.0)) * 100)
        progress.seen_points.add(point)
        return progress

    def add_progress(self, **kwargs):
        return self.client.post(
            reverse(
                get_all_post_progress_name,
                kwargs={
                    version_key: v1_key
                }
            ),
            data=json.dumps(kwargs[data_key]),
            content_type=content_type
        )

    def post_progress_batch(self, data):
        return self.client.put(
            reverse(
                post_progress_batch_name,
                kwargs={
                    version_key: v1_key,
                },
            ),
            data=json.dumps(data),
            content_type=content_type
        )

    def fetch_progress_seen_points(self, pk):
        url = reverse(
            get_progress_name,
            kwargs={
                version_key: v1_key,
                pk_key: pk
            },
        )
        return self.client.get(url)

    def fetch_all_progress_seen_points(self):
        url = reverse(
            get_all_post_progress_name,
            kwargs={
                version_key: v1_key
            },
        )
        return self.client.get(url)







    # STARRED

    @staticmethod
    def create_starred_list(user, debate):
        starred = Starred.objects.create(user=user)
        starred.starred_list.add(debate)
        return starred

    def post_starred_request(self, data):
        return self.client.post(
            reverse(
                starred_name,
                kwargs={
                    version_key: v1_key,
                },
            ),
            data=json.dumps(data),
            content_type=content_type
        )

    def fetch_starred_list(self):
        url = reverse(
            starred_name,
            kwargs={
                version_key: v1_key
            }
        )
        return self.client.get(url)











    # AUTH

    def login_a_user(self, email, password):
        url = reverse(
            auth_token_obtain_name,
            kwargs={
                version_key: v1_key
            }
        )
        return self.client.post(
            url,
            data=json.dumps({
                username_key: email,
                password_key: password
            }),
            content_type=content_type
        )

    def refresh_token(self, token):
        url = reverse(
            auth_token_refresh_name,
            kwargs={
                version_key: v1_key
            }
        )
        return self.client.post(
            url,
            data=json.dumps({
                refresh_key: token
            }),
            content_type=content_type
        )

    def delete_user(self, user):
        view = DeleteUserView.as_view()
        url = reverse(
            auth_delete_name,
            kwargs={
                version_key: v1_key
            }
        )
        request = self.requestFactory.post(
            url,
            content_type=content_type
        )
        force_authenticate(request, user=user)

        return view(request)

    def change_user_password(self, old_password, new_password):
        url = reverse(
            auth_change_password_name,
            kwargs={
                version_key: v1_key
            }
        )
        return self.client.put(
            url,
            data=json.dumps({
                old_password_key: old_password,
                new_password_key: new_password
            }),
            content_type=content_type
        )

    def change_user_email(self, user, new_email):
        view = ChangeEmailView.as_view()
        url = reverse(
            auth_change_email_name,
            kwargs={
                version_key: v1_key
            }
        )
        request = self.requestFactory.put(
            url,
            data=json.dumps({
                new_email_key: new_email
            }),
            content_type=content_type
        )
        force_authenticate(request, user=user)

        return view(request)

    def get_current_email(self, user):
        view = GetCurrentEmailView.as_view()
        url = reverse(
            auth_get_current_email_name,
            kwargs={
                version_key: v1_key
            }
        )
        request = self.requestFactory.get(url)
        force_authenticate(request, user=user)

        return view(request)

    def login_client(self, username, password):
        url = reverse(
            auth_token_obtain_name,
            kwargs={
                version_key: v1_key
            }
        )
        # get a token from DRF
        response = self.client.post(
            url,
            data=json.dumps(
                {
                    username_key: username,
                    password_key: password
                }
            ),
            content_type=content_type
        )
        self.token = response.data[access_key]
        # set the token in the header
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.token
        )
        self.client.login(username=username, password=password)
        return self.token

    def register_a_user(self, email, password):
        return self.client.post(
            reverse(
                auth_register_name,
                kwargs={
                    version_key: v1_key
                }
            ),
            data=json.dumps(
                {
                    email_key: email,
                    password_key: password
                }
            ),
            content_type=content_type
        )









    def setUp(self):

        # create a user

        self.user = User.objects.create_user(
            username="test@mail.com",
            email="test@mail.com",
            password="testing"
        )
        self.today = datetime.today()
        self.requestFactory = APIRequestFactory()


        # add test data

        self.gun_control = Debate.objects.create(title="Should we ban assault rifles?", short_title="Assault rifle ban", last_updated=self.today, total_points=2, tags="gun control, school shootings")
        self.gun_control_point_1 = Point.objects.create(debate=self.gun_control, description="Civilians can't own tanks though")
        self.gun_control_point_2 = Point.objects.create(debate=self.gun_control, description="But the 2nd amendment")
        self.create_progress_point(self.user, self.gun_control, self.gun_control_point_1)

        self.abortion = Debate.objects.create(title="Is it a woman's right to choose?", short_title="Abortion rights", last_updated=self.today, total_points=1)
        self.abortionPoint = Point.objects.create(debate=self.abortion, description="Is it a woman's right to choose?")
        self.abortionPointImage = PointImage.objects.create(point=self.abortionPoint, source="Reuters", url="www.reuters.com/image")
        self.abortionPointHyperlink = PointHyperlink.objects.create(point=self.abortionPoint, substring="a woman's right to", url="www.vox.com/abortion")
        self.create_progress_point(self.user, self.abortion, self.abortionPoint)

        self.border_wall = Debate.objects.create(title="Is the border wall an effective idea?", short_title="Border wall", last_updated=self.today, total_points=1)
        self.border_wall_point = Point.objects.create(debate=self.border_wall, description="Is it an effective border security tool?")

        self.vetting = Debate.objects.create(title="Are we doing enough vetting?", short_title="Vetting", last_updated=self.today, total_points=1)
        self.vetting_point = Point.objects.create(debate=self.vetting, description="Are we doing enough?")

        self.starred_list = self.create_starred_list(self.user, self.gun_control)


# DEBATES

class DebateModelTest(BaseViewTest):
    def test_basic_create_a_debate(self):
        debate = Debate.objects.create(
            title="Test debate",
            last_updated=self.today,
            total_points=1
        )
        self.assertEqual(debate.title, "Test debate")
        self.assertEqual(debate.last_updated, self.today)

class GetAllDebatesTest(BaseViewTest):

    def test_get_all_debates(self):
        response = self.filter_debates({})
        expected = Debate.objects.all()
        serialized = DebateFilterSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class FilterDebatesTest(BaseViewTest):

    def test_filter_debates(self):
        expected = Debate.objects.all().filter(pk=self.gun_control.pk)

        response = self.filter_debates({
            search_string_key: "gun"
        })
        serialized = DebateFilterSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.filter_debates({
            filter_key: starred_filter_value,
            all_starred_key: [self.gun_control.pk],
        })
        serialized = DebateFilterSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.filter_debates({
            search_string_key: "gun",
            filter_key: starred_filter_value,
            all_starred_key: [self.gun_control.pk]
        })
        serialized = DebateFilterSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.filter_debates({
            search_string_key: "gun",
            filter_key: progress_filter_value,
            all_progress_key: [self.gun_control.pk]
        })
        serialized = DebateFilterSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.filter_debates({
            search_string_key: "gun",
            filter_key: no_progress_filter_value,
            all_progress_key: [self.gun_control.pk]
        })
        self.assertEqual(response.data, [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.filter_debates({
            search_string_key: "gun",
            filter_key: last_updated_filter_value
        })
        serialized = DebateFilterSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.filter_debates({
            search_string_key: "gun",
            filter_key: random_filter_value
        })
        serialized = DebateFilterSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.filter_debates({
            search_string_key: ""
        })
        self.assertEqual(
            response.data[message_key],
            debate_filter_invalid_search_string_error
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.filter_debates({
            filter_key: "starredd",
            all_starred_key: [self.gun_control.pk],
        })
        self.assertEqual(
            response.data[message_key],
            debate_filter_unknown_filter_error
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.filter_debates({
            filter_key: 1,
            all_starred_key: [self.gun_control.pk],
        })
        self.assertEqual(
            response.data[message_key],
            debate_filter_invalid_filter_format_error
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.filter_debates({
            filter_key: starred_filter_value,
            all_starred_key: 1,
        })
        self.assertEqual(
            response.data[message_key],
            debate_filter_invalid_pk_array_format_error
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.filter_debates({
            filter_key: starred_filter_value,
            all_starred_key: ["1"],
        })
        self.assertEqual(
            response.data[message_key],
            debate_filter_invalid_pk_array_items_format_error
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.filter_debates({
            filter_key: starred_filter_value
        })
        self.assertEqual(
            response.data[message_key],
            debate_filter_missing_pk_array_error.format(starred_filter_value)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetASingleDebateTest(BaseViewTest):

    def test_get_a_debate(self):
        valid_debate = Debate.objects.get(pk=self.gun_control.pk)
        serialized = DebateSerializer(valid_debate)
        response = self.fetch_a_debate(valid_debate.pk)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.fetch_a_debate(valid_debate.pk)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.fetch_a_debate(100000000000)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)







# PROGRESS

class ProgressModelTest(BaseViewTest):
    def test_basic_create_a_progress_point(self):
        progress_point = Progress.objects.get(user=self.user, debate=self.gun_control)

        self.assertEqual(progress_point.user.username, "test@mail.com")
        self.assertEqual(progress_point.debate.title, "Should we ban assault rifles?")
        self.assertEqual(progress_point.completed_percentage, 50)
        self.assertEqual(progress_point.seen_points.all()[0].pk, self.gun_control_point_1.pk)

class AddProgressPointTest(BaseViewTest):

    def test_create_a_progress_point(self):
        self.login_client('test@mail.com', 'testing')
        response = self.add_progress(
            kind=post_key,
            version_key=v1_key,
            data={
                    debate_pk_key: self.gun_control.pk,
                    point_pk_key: self.gun_control_point_2.pk
                 }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.fetch_progress_seen_points(self.gun_control.pk)
        self.assertEqual(response.data[completed_percentage_key], 100)

        response = self.add_progress(
            kind=post_key,
            version_key=v1_key,
            data={
                    debate_pk_key: "",
                    point_pk_key: ""
                 }
        )
        self.assertEqual(
            response.data[message_key],
            progress_point_post_error
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class AddProgressPointBatchTest(BaseViewTest):

    def test_create_a_progress_point_batch(self):
        self.login_client('test@mail.com', 'testing')
        response = self.post_progress_batch(data={
            all_debate_points_key: [
                {
                    debate_key: self.vetting.pk,
                    seen_points_key: [self.vetting_point.pk]
                }
            ]
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.fetch_progress_seen_points(self.vetting.pk)
        self.assertEqual(response.data[completed_percentage_key], 100)

        response = self.post_progress_batch(data={
            all_debate_points_key: [
                {
                    "incorrect_key": self.vetting.pk,
                    seen_points_key: ""
                }
            ]
        })
        self.assertEqual(
            response.data[message_key],
            progress_point_batch_post_error
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetASingleDebateProgressPointsTest(BaseViewTest):

    def test_get_debate_progress_points(self):
        valid_progress = Progress.objects.get(user=self.user, debate=self.gun_control)
        self.login_client('test@mail.com', 'testing')
        response = self.fetch_progress_seen_points(valid_progress.debate.pk)
        serialized = ProgressSerializer(valid_progress)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.fetch_progress_seen_points(10000000000)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.fetch_progress_seen_points(self.vetting.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class GetAllDebateProgressPointsTest(BaseViewTest):

    def test_get_all_debate_progress_points(self):
        valid_progress = Progress.objects.filter(user=self.user)
        self.login_client('test@mail.com', 'testing')
        response = self.fetch_all_progress_seen_points()
        serialized = ProgressAllSerializer(valid_progress, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)







# STARRED

class StarredModelTest(BaseViewTest):
    def test_basic_create_a_starred_list(self):
        starred_list = Starred.objects.create(user=self.user)
        starred_list.starred_list.add(self.gun_control)
        self.assertTrue(starred_list.starred_list.filter(pk=self.gun_control.pk).exists())

class AddStarredTest(BaseViewTest):

    def test_star_unstar_debates(self):
        self.login_client('test@mail.com', 'testing')
        response = self.post_starred_request(
            data={
                    starred_list_key: [self.border_wall.pk, self.abortion.pk],
                    unstarred_list_key: [self.abortion.pk]
                 }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.fetch_starred_list()
        self.assertTrue(self.border_wall.pk in response.data[starred_list_key])
        self.assertTrue(self.abortion.pk not in response.data[starred_list_key])

        response = self.post_starred_request(
            data={
                    starred_list_key: [],
                    unstarred_list_key: [self.border_wall.pk]
                 }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.fetch_starred_list()
        self.assertFalse(self.border_wall.pk in response.data[starred_list_key])

        response = self.post_starred_request(
            data={
                    starred_list_key: [],
                    unstarred_list_key: []
                 }
        )
        self.assertEqual(
            response.data[message_key],
            starred_post_empty_error
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.post_starred_request(
            data={
                    starred_list_key: ["1"],
                    unstarred_list_key: []
                 }
        )
        self.assertEqual(
            response.data[message_key],
            starred_post_format_error
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetStarredTest(BaseViewTest):

    def test_starred_list(self):
        valid_starred_list = Starred.objects.get(user=self.user)
        self.login_client('test@mail.com', 'testing')
        response = self.fetch_starred_list()
        expected = Starred.objects.get(user=valid_starred_list.user)
        serialized = StarredSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)







# AUTH

class AuthChangeEmailTest(BaseViewTest):

    def test_change_email(self):
        change_email_user = User.objects.create_user(
            username="change_email_user@mail.com",
            email="change_email_user@mail.com",
            password="change_email_pass"
        )
        self.login_a_user("change_email_user@mail.com", "change_email_pass")
        response = self.change_user_email(change_email_user, change_email_user.email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data[message_key],
            already_using_email_error
        )
        response = self.change_user_email(change_email_user, "change_email_user1@mail.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            success_response
        )
        response = self.login_a_user("invalidemail@mail.com", "invalidpass")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthGetCurrentEmailTest(BaseViewTest):

    def test_change_email(self):
        get_current_email_user = User.objects.create_user(
            username="get_current_email_user@mail.com",
            password="get_current_email_pass"
        )
        self.login_a_user("get_current_email_user@mail.com", "get_current_email_pass")
        response = self.get_current_email(get_current_email_user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[current_email_key], "get_current_email_user@mail.com")
        self.assertFalse(response.data[is_verified_key])

class AuthChangePasswordTest(BaseViewTest):

    def test_change_password(self):
        self.login_client('test@mail.com', 'testing')
        response = self.change_user_password("testing", "testing1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            success_response
        )

        response = self.change_user_password("testing", "afeeaaeve")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class AuthLoginUserTest(BaseViewTest):

    def test_login_user_with_valid_credentials(self):
        response = self.login_a_user("test@mail.com", "testing")
        self.assertIn(access_key, response.data)
        self.assertIn(refresh_key, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.refresh_token(response.data[refresh_key])
        self.assertIn(access_key, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.login_a_user("invalidusername", "invalidpass")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthRegisterUserTest(BaseViewTest):

    def test_register_a_user(self):
        response = self.register_a_user("new_user@mail.com", "new_pass")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.register_a_user("", "")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class DeleteUserTest(BaseViewTest):

    def test_delete_user(self):
        deleteUser = User.objects.create_user(
            username="todelete_user@mail.com",
            email="todelete_user@mail.com",
            password="todelete_pass"
        )
        response = self.login_a_user("todelete_user@mail.com", "todelete_pass")
        self.assertIn(access_key, response.data)
        self.assertIn(refresh_key, response.data)

        response = self.delete_user(deleteUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.login_a_user("todelete_user@mail.com", "todelete_pass")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
