username_keyfrom django.test import TestCase
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
    def create_debate(title="", last_updated=None, debate_map=None):
        if title != "" and last_updated != None and debate_map != None:
            return Debate.objects.create(title=title, last_updated=last_updated, debate_map=debate_map)

    @staticmethod
    def create_progress_point(user=None, debate=None, debate_point_key=""):
        if user != None and debate != None and debate_point_key != "":
            Progress.objects.create(user=user, debate=debate, seen_points=[debate_point_key])

    @staticmethod
    def create_starred_list(user=None, debate=None):
        if user != None and debate != None:
            starred = Starred.objects.create(user=user)
            starred.starred_list.add(debate)

    def make_a_create_progress_request(self, kind=post_key, **kwargs):
        """
        Make a post request to create a progress point
        :param kind: HTTP VERB
        :return:
        """
        if kind == post_key:
            return self.client.post(
                reverse(
                    post_progress_name,
                    kwargs={
                        version_key: kwargs[version_key]
                    }
                ),
                data=json.dumps(kwargs[data]),
                content_type=content_type
            )
        else:
            return None

    def make_a_create_starred_list_request(self, kind=post_key, **kwargs):
        """
        Make a post request to create/add to a reading list
        :param kind: HTTP VERB
        :return:
        """
        if kind == post_key:
            return self.client.post(
                reverse(
                    post_starred_list_name,
                    kwargs={
                        version_key: kwargs[version_key]
                    }
                ),
                data=json.dumps(kwargs[data]),
                content_type=content_type
            )
        else:
            return None

    def set_progress_point_completed_request(self, kind=post_key, **kwargs):
        """
        Make a post request to set a progress point as completed
        :param kind: HTTP VERB
        :return:
        """
        if kind == post_key:
            return self.client.post(
                reverse(
                    post_progress_completed_name,
                    kwargs={
                        version_key: kwargs[version_key]
                    }
                ),
                data=json.dumps(kwargs[data]),
                content_type=content_type
            )
        else:
            return None

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
            get_starred_list_name,
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
                password: password
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
                old_password: old_password,
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
        self.gunControl = self.create_debate("Gun control", self.today, {"Should we ban assault rifles?" : ["rebuttal"]})
        self.abortion = self.create_debate("Abortion", self.today, {"Is it a woman's right to choose?" : ["rebuttal"]})
        self.borderWall = self.create_debate("The border wall", self.today, {"Is it an effective border security tool?" : ["rebuttal"]})
        self.vetting = self.create_debate("Vetting", self.today, {"Are we doing enough?" : ["rebuttal"]})

        self.create_progress_point(self.user, self.gunControl, "Civilians can't own tanks though.")
        self.create_progress_point(self.user, self.abortion, "We allow parents to refuse to donate organs to their child.")
        self.create_progress_point(self.user, self.borderWall, "Drones cost 1/100th of the price.")

        self.starred_list = self.create_starred_list(self.user, self.gunControl)

        self.valid_progress_point_data = {
            debate_pk_key: self.gunControl.pk,
            debate_point_key: "Civilians can't own tanks though."
        }
        self.valid_progress_point_completed_data = {
            debate_pk_key: self.gunControl.pk,
            completed_key: True
        }
        self.invalid_progress_point_data_empty = {
            debate_pk_key: "",
            debate_point_key: ""
        }
        self.invalid_progress_point_completed_data_empty = {
            debate_pk_key: "",
            completed_key: ""
        }

        self.valid_starred_list_data = {
            debate_pk_key: self.abortion.pk,
        }
        self.invalid_starred_list_data_empty = {
            debate_pk_key: "",
        }
        self.invalid_starred_list_data = {
            debate_pk_key: 100000000000,
        }

class ProgressModelTest(BaseViewTest):
    def test_basic_create_a_progress_point(self):
        """"
        This test ensures that the progress point created exists
        """
        progress_point = Progress.objects.get(user=self.user, debate=self.gunControl)

        self.assertEqual(progress_point.user.username, "test@mail.com")
        self.assertEqual(progress_point.debate.title, "Gun control")
        self.assertEqual(progress_point.completed, False)
        self.assertEqual(progress_point.seen_points, ["Civilians can't own tanks though."])
        self.assertEqual(str(progress_point), "test@mail.com - Gun control")

class DebateModelTest(BaseViewTest):
    def test_basic_create_a_debate(self):
        """"
        This test ensures that the debate created exists
        """
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
        """"
        This test ensures that the reading list created exists
        """
        starred_list = Starred.objects.create(user=self.user)
        starred_list.starred_list.add(self.gunControl)
        self.assertTrue(starred_list.starred_list.filter(pk=self.gunControl.pk).exists())
        self.assertEqual(str(starred_list), "test@mail.com - Gun control")

class GetAllDebatesTest(BaseViewTest):

    def test_get_all_debates(self):
        """
        This test ensures that all debate added in the setUp method
        exist when we make a GET request to the debate/ endpoint
        """
        # hit the API endpoint
        response = self.client.get(
            reverse(get_all_debates_name, kwargs={version_key: v1_key})
        )
        # fetch the data from db
        expected = Debate.objects.all()
        serialized = DebateSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetASingleDebateTest(BaseViewTest):

    def test_get_a_debate(self):
        """
        This test ensures that a single debate of a given title is
        returned
        """
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
        self.assertEqual(
            response.data[message_key],
            "Debate with ID: 100000000000 does not exist"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class AddProgressPointTest(BaseViewTest):

    def test_create_a_progress_point(self):
        """
        This test ensures that a single progress point can be added
        """
        self.login_client('test@mail.com', 'testing')
        # hit the API endpoint
        response = self.make_a_create_progress_request(
            kind=post_key,
            version_key=v1_key,
            data=self.valid_progress_point_data
        )
        self.assertEqual(response.data[seen_points_key][-1], self.valid_progress_point_data[debate_point_key])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test with invalid data
        response = self.make_a_create_progress_request(
            kind=post_key,
            version_key=v1_key,
            data=self.invalid_progress_point_data_empty
        )
        self.assertEqual(
            response.data[message_key],
            "Both debate ID and debate point are required to add a progress point"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class SetProgressPointCompletedTest(BaseViewTest):

    def test_set_progress_point_completed(self):
        """
        This test ensures that a single progress point can be set as completed
        """
        self.login_client('test@mail.com', 'testing')
        # hit the API endpoint
        response = self.set_progress_point_completed_request(
            kind=post_key,
            version_key=v1_key,
            data=self.valid_progress_point_completed_data
        )
        self.assertTrue(response.data[completed_key])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test with invalid data
        response = self.set_progress_point_completed_request(
            kind=post_key,
            version_key=v1_key,
            data=self.invalid_progress_point_completed_data_empty
        )
        self.assertEqual(
            response.data[message_key],
            "Both debate ID and completed status are required to update completed status"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetASingleProgressPointTest(BaseViewTest):

    def test_get_a_progress_point(self):
        """
        This test ensures that a single progress point of a given debate title is returned
        """
        valid_progress = Progress.objects.get(user=self.user, debate=self.gunControl)
        self.login_client('test@mail.com', 'testing')
        # hit the API endpoint
        response = self.fetch_progress_seen_points(valid_progress.debate.pk)
        # fetch the data from db
        expected = Progress.objects.get(user=valid_progress.user, debate=valid_progress.debate)
        serialized = ProgressSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test with a debate that does not exist
        response = self.fetch_progress_seen_points(10000000000)
        self.assertEqual(
            response.data[message_key],
            "Could not find debate with ID 10000000000"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # test with a progress point that does not exist
        response = self.fetch_progress_seen_points(self.vetting.pk)
        self.assertEqual(
            response.data[message_key],
            "Could not retrieve progress"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class GetAllProgressPointsTest(BaseViewTest):

    def test_get_all_progress_points(self):
        """
        This test ensures that a all progress points can be returned
        """
        valid_progress = Progress.objects.filter(user=self.user)
        self.login_client('test@mail.com', 'testing')
        # hit the API endpoint
        response = self.fetch_all_progress_seen_points()
        # fetch the data from db
        serialized = ProgressSerializer(valid_progress, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class AddToStarredTest(BaseViewTest):

    def test_create_a_starred_list(self):
        """
        This test ensures that a single debate can be added to the reading list
        """
        self.login_client('test@mail.com', 'testing')
        # hit the API endpoint
        response = self.make_a_create_starred_list_request(
            kind=post_key,
            version_key=v1_key,
            data=self.valid_starred_list_data
        )
        self.assertTrue(self.abortion.pk in response.data[starred_list_key])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test with invalid data
        response = self.make_a_create_starred_list_request(
            kind=post_key,
            version_key=v1_key,
            data=self.invalid_starred_list_data_empty
        )
        self.assertEqual(
            response.data[message_key],
            "A debate ID is required"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # test with a debate that does not exist
        response = self.make_a_create_starred_list_request(
            kind=post_key,
            version_key=v1_key,
            data=self.invalid_starred_list_data
        )
        self.assertEqual(
            response.data[message_key],
            "Could not find debate with ID 100000000000"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetASingleStarredTest(BaseViewTest):

    def test_get_a_starred_list(self):
        """
        This test ensures that a single progress point of a given debate title is returned
        """
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
    """
    Tests for the auth/change-email/ endpoint
    """

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
    """
    Tests for the auth/change-password/ endpoint
    """

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
    """
    Tests for the auth/token/obtain endpoint
    """

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
    """
    Tests for auth/register/ endpoint
    """
    def test_register_a_user_with_valid_data(self):
        response = self.register_a_user("new_user@mail.com", "new_pass")
        # assert status code is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_a_user_with_invalid_data(self):
        response = self.register_a_user("", "")
        # assert status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class DeleteUserTest(BaseViewTest):
    """
    Tests for the auth/token/obtain endpoint
    """

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
