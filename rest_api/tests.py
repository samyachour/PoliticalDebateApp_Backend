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

    @staticmethod
    def create_debate(title="", last_updated=None, debate_map=None, total_points=0):
        if title != "" and last_updated != None and debate_map != None:
            return Debate.objects.create(title=title, last_updated=last_updated, debate_map=debate_map, total_points=total_points)

    @staticmethod
    def create_progress_point(user=None, debate=None, debate_point_key=""):
        if user != None and debate != None and debate_point_key != "":
            Progress.objects.create(user=user, debate=debate, seen_points=[debate_point_key])

    @staticmethod
    def create_starred_list(user=None, debate=None):
        if user != None and debate != None:
            starred = Starred.objects.create(user=user)
            starred.starred_list.add(debate)

    def create_progress(self, kind=post_key, **kwargs):
        if kind == post_key:
            return self.client.post(
                reverse(
                    post_progress_name,
                    kwargs={
                        version_key: v1_key
                    }
                ),
                data=json.dumps(kwargs[data_key]),
                content_type=content_type
            )
        else:
            return None

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

    def search_debates(self, search_string=""):
        url = reverse(
            search_debates_name,
            kwargs={
                version_key: v1_key,
                search_string_key: search_string
            },
        )
        return self.client.get(url)

    def fetch_a_debate(self, pk=None):
        url = reverse(
            get_debate_name,
            kwargs={
                version_key: v1_key,
                pk_key: pk
            },
        )
        return self.client.get(url)

    def fetch_progress_seen_points(self, pk=""):
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
            get_all_progress_name,
            kwargs={
                version_key: v1_key
            },
        )
        return self.client.get(url)

    def fetch_starred_list(self):
        url = reverse(
            starred_name,
            kwargs={
                version_key: v1_key
            }
        )
        return self.client.get(url)

    def login_a_user(self, email="", password=""):
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

    def refresh_token(self, token=""):
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
        view = DeleteUsersView.as_view()
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

    def change_user_password(self, old_password="", new_password=""):
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

    def change_user_email(self, user, new_email=""):
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

    def login_client(self, username="", password=""):
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

    def register_a_user(self, email="", password=""):
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

        self.requestFactory = APIRequestFactory()

        # create a admin user
        self.user = User.objects.create_superuser(
            username="test@mail.com",
            email="test@mail.com",
            password="testing"
        )
        self.today = datetime.today()
        # add test data
        self.gunControl = self.create_debate("Gun control", self.today, {"Should we ban assault rifles?" : "rebuttal", "Civilians can't own tanks though.": "rebuttal"}, 2)
        self.abortion = self.create_debate("Abortion", self.today, {"Is it a woman's right to choose?" : "rebuttal"}, 1)
        self.borderWall = self.create_debate("The border wall", self.today, {"Is it an effective border security tool?" : "rebuttal"}, 1)
        self.vetting = self.create_debate("Vetting", self.today, {"Are we doing enough?" : "rebuttal"}, 1)

        self.create_progress_point(self.user, self.gunControl, "Civilians can't own tanks though.")
        self.create_progress_point(self.user, self.abortion, "Is it a woman's right to choose?")
        self.create_progress_point(self.user, self.borderWall, "Is it an effective border security tool?")

        self.starred_list = self.create_starred_list(self.user, self.gunControl)

        self.valid_progress_point_data = {
            pk_key: self.gunControl.pk,
            debate_point_key: "Should we ban assault rifles?"
        }
        self.invalid_progress_point_data_empty = {
            pk_key: "",
            debate_point_key: ""
        }

        self.valid_starred_data = {
            starred_list_key: [self.borderWall.pk, self.abortion.pk],
            unstarred_list_key: []
        }
        self.valid_unstarred_data = {
            starred_list_key: [],
            unstarred_list_key: [self.abortion.pk]
        }
        self.invalid_starred_data_empty = {
            starred_list_key: [],
            unstarred_list_key: []
        }
        self.invalid_starred_data = {
            starred_list_key: ["1"],
            unstarred_list_key: []
        }

class ProgressModelTest(BaseViewTest):
    def test_basic_create_a_progress_point(self):
        progress_point = Progress.objects.get(user=self.user, debate=self.gunControl)

        self.assertEqual(progress_point.user.username, "test@mail.com")
        self.assertEqual(progress_point.debate.title, "Gun control")
        self.assertEqual(progress_point.completed, False)
        self.assertEqual(progress_point.seen_points, ["Civilians can't own tanks though."])
        self.assertEqual(str(progress_point), "test@mail.com - Gun control")

class DebateModelTest(BaseViewTest):
    def test_basic_create_a_debate(self):
        debate = Debate.objects.create(
            title="Test debate",
            last_updated=self.today,
            debate_map={"Test point": ["rebuttal"]}
        )
        self.assertEqual(debate.title, "Test debate")
        self.assertEqual(debate.last_updated, self.today)
        self.assertEqual(debate.debate_map, {"Test point": ["rebuttal"]})
        self.assertEqual(str(debate), "Test debate updated {}".format(self.today))

class StarredModelTest(BaseViewTest):
    def test_basic_create_a_starred_list(self):
        starred_list = Starred.objects.create(user=self.user)
        starred_list.starred_list.add(self.gunControl)
        self.assertTrue(starred_list.starred_list.filter(pk=self.gunControl.pk).exists())
        self.assertEqual(str(starred_list), "test@mail.com - Gun control")

class GetAllDebatesTest(BaseViewTest):

    def test_get_all_debates(self):
        # hit the API endpoint
        response = self.client.get(
            reverse(search_debates_name, kwargs={version_key: v1_key})
        )
        # fetch the data from db
        expected = Debate.objects.all()
        serialized = DebateSearchSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class SearchDebatesTest(BaseViewTest):

    def test_search_debates(self):
        response = self.search_debates("gun")
        # fetch the data from db
        expected = Debate.objects.all().filter(title="Gun control")
        serialized = DebateSearchSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetASingleDebateTest(BaseViewTest):

    def test_get_a_debate(self):
        valid_debate = Debate.objects.get(pk=self.gunControl.pk)
        serialized = DebateSerializer(valid_debate)
        # hit the API endpoint
        response = self.fetch_a_debate(valid_debate.pk)
        # fetch the data from db
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # hit the API endpoint
        response = self.fetch_a_debate(valid_debate.pk)
        # fetch the data from db
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test with a debate that does not exist
        response = self.fetch_a_debate(100000000000)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class AddProgressPointTest(BaseViewTest):

    def test_create_a_progress_point(self):
        self.login_client('test@mail.com', 'testing')
        # hit the API endpoint
        response = self.create_progress(
            kind=post_key,
            version_key=v1_key,
            data=self.valid_progress_point_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.fetch_progress_seen_points(self.valid_progress_point_data[pk_key])
        self.assertTrue(response.data[completed_key])
        # test with invalid data
        response = self.create_progress(
            kind=post_key,
            version_key=v1_key,
            data=self.invalid_progress_point_data_empty
        )
        self.assertEqual(
            response.data[message_key],
            progress_point_post_error
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetASingleDebateProgressPointsTest(BaseViewTest):

    def test_get_debate_progress_points(self):
        valid_progress = Progress.objects.get(user=self.user, debate=self.gunControl)
        self.login_client('test@mail.com', 'testing')
        # hit the API endpoint
        response = self.fetch_progress_seen_points(valid_progress.debate.pk)
        # fetch the data from db
        serialized = ProgressSerializer(valid_progress)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test with a debate that does not exist
        response = self.fetch_progress_seen_points(10000000000)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # test with a progress point that does not exist
        response = self.fetch_progress_seen_points(self.vetting.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class GetAllDebateProgressPointsTest(BaseViewTest):

    def test_get_all_debate_progress_points(self):
        valid_progress = Progress.objects.filter(user=self.user)
        self.login_client('test@mail.com', 'testing')
        # hit the API endpoint
        response = self.fetch_all_progress_seen_points()
        # fetch the data from db
        serialized = ProgressSerializer(valid_progress, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class AddStarredTest(BaseViewTest):

    def test_star_unstar_debates(self):
        self.login_client('test@mail.com', 'testing')
        # star debates
        response = self.post_starred_request(
            data=self.valid_starred_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.fetch_starred_list()
        self.assertTrue(self.borderWall.pk in response.data[starred_list_key])
        self.assertTrue(self.abortion.pk in response.data[starred_list_key])
        # unstar debate
        response = self.post_starred_request(
            data=self.valid_unstarred_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.fetch_starred_list()
        self.assertFalse(self.abortion.pk in response.data[starred_list_key])
        # test with invalid data
        response = self.post_starred_request(
            data=self.invalid_starred_data_empty
        )
        self.assertEqual(
            response.data[message_key],
            starred_post_empty_error
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # test with a string array
        response = self.post_starred_request(
            data=self.invalid_starred_data
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
        # hit the API endpoint
        response = self.fetch_starred_list()
        # fetch the data from db
        expected = Starred.objects.get(user=valid_starred_list.user)
        serialized = StarredSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class AuthChangeEmailTest(BaseViewTest):

    def test_change_email(self):
        changeEmailUser = User.objects.create_superuser(
            username="changeemail_user@mail.com",
            email="changeemail_user@mail.com",
            password="changeemail_pass"
        )
        # test login with valid credentials
        self.login_a_user("changeemail_user@mail.com", "changeemail_pass")
        response = self.change_user_email(changeEmailUser, "changeemail_user1@mail.com")
        # assert status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            "Success."
        )
        # test with incorrect old email
        response = self.login_a_user("changeemail_user@mail.com", "changeemail_pass")
        # assert status code is 400 Bad request
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthChangePasswordTest(BaseViewTest):

    def test_change_password(self):
        # test login with valid credentials
        self.login_client('test@mail.com', 'testing')
        response = self.change_user_password("testing", "testing1")
        # assert status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            "Success."
        )
        # test with incorrect old password
        response = self.change_user_password("adhwuwf", "afeeaaeve")
        # assert status code is 400 Bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class AuthLoginUserTest(BaseViewTest):

    def test_login_user_with_valid_credentials(self):
        # test login with valid credentials
        response = self.login_a_user("test@mail.com", "testing")
        # assert access token key exists
        self.assertIn(access_key, response.data)
        # assert refresh_key token key exists
        self.assertIn(refresh_key, response.data)
        # assert status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # refresh token
        response = self.refresh_token(response.data[refresh_key])
        # assert token key exists
        self.assertIn(access_key, response.data)
        # assert status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test login with invalid credentials
        response = self.login_a_user("anonymous", "pass")
        # assert status code is 401 UNAUTHORIZED
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthRegisterUserTest(BaseViewTest):

    def test_register_a_user_with_valid_data(self):
        response = self.register_a_user("new_user@mail.com", "new_pass")
        # assert status code is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_a_user_with_invalid_data(self):
        response = self.register_a_user("", "")
        # assert status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class DeleteUserTest(BaseViewTest):

    def test_delete_user(self):
        deleteUser = User.objects.create_superuser(
            username="todelete_user@mail.com",
            email="todelete_user@mail.com",
            password="todelete_pass"
        )
        # test login with valid credentials
        response = self.login_a_user("todelete_user@mail.com", "todelete_pass")
        # assert access token key exists
        self.assertIn(access_key, response.data)
        # assert refresh token key exists
        self.assertIn(refresh_key, response.data)
        # delete user
        response = self.delete_user(deleteUser)
        # assert status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test login with invalid credentials
        response = self.login_a_user("todelete_user@mail.com", "todelete_pass")
        # assert status code is 401 UNAUTHORIZED
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
