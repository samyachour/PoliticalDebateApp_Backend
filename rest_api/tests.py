from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from rest_api.models import *
from .serializers import *
import json

# tests for views

class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_debate(title="", subtitle=""):
        if title != "" and subtitle != "":
            return Debate.objects.create(title=title, subtitle=subtitle)

    @staticmethod
    def create_progress_point(user=None, debate=None, debate_point=""):
        if user != None and debate != None and debate_point != "":
            Progress.objects.create(user=user, debate=debate, seen_points=[debate_point])

    @staticmethod
    def create_starred_list(user=None, debate=None):
        if user != None and debate != None:
            starred = Starred.objects.create(user=user)
            starred.starred_list.add(debate)

    def make_a_create_progress_request(self, kind="post", **kwargs):
        """
        Make a post request to create a progress point
        :param kind: HTTP VERB
        :return:
        """
        if kind == "post":
            return self.client.post(
                reverse(
                    "post-progress",
                    kwargs={
                        "version": kwargs["version"]
                    }
                ),
                data=json.dumps(kwargs["data"]),
                content_type='application/json'
            )
        else:
            return None

    def make_a_create_starred_list_request(self, kind="post", **kwargs):
        """
        Make a post request to create/add to a reading list
        :param kind: HTTP VERB
        :return:
        """
        if kind == "post":
            return self.client.post(
                reverse(
                    "post-starred-list",
                    kwargs={
                        "version": kwargs["version"]
                    }
                ),
                data=json.dumps(kwargs["data"]),
                content_type='application/json'
            )
        else:
            return None

    def set_progress_point_completed_request(self, kind="post", **kwargs):
        """
        Make a post request to set a progress point as completed
        :param kind: HTTP VERB
        :return:
        """
        if kind == "post":
            return self.client.post(
                reverse(
                    "post-progress-completed",
                    kwargs={
                        "version": kwargs["version"]
                    }
                ),
                data=json.dumps(kwargs["data"]),
                content_type='application/json'
            )
        else:
            return None

    def fetch_a_debate(self, pk=None):
        url = reverse(
            "get-debate",
            kwargs={
                "version": "v1",
                "pk": pk
            },
        )
        return self.client.get(url)

    def fetch_progress_seen_points(self, pk=""):
        url = reverse(
            "get-progress",
            kwargs={
                "version": "v1",
                "pk": pk
            },
        )
        return self.client.get(url)

    def fetch_all_progress_seen_points(self):
        url = reverse(
            "get-all-progress",
            kwargs={
                "version": "v1"
            },
        )
        return self.client.get(url)

    def fetch_starred_list(self):
        url = reverse(
            "get-starred-list",
            kwargs={
                "version": "v1"
            }
        )
        return self.client.get(url)

    def login_a_user(self, username="", password=""):
        url = reverse(
            "auth-login",
            kwargs={
                "version": "v1"
            }
        )
        return self.client.post(
            url,
            data=json.dumps({
                "username": username,
                "password": password
            }),
            content_type="application/json"
        )

    def refresh_token(self, token=""):
        url = reverse(
            "auth-refresh-token",
            kwargs={
                "version": "v1"
            }
        )
        return self.client.post(
            url,
            data=json.dumps({
                "token": token
            }),
            content_type="application/json"
        )

    def change_user_password(self, old_password="", new_password=""):
        url = reverse(
            "auth-change-password",
            kwargs={
                "version": "v1"
            }
        )
        return self.client.put(
            url,
            data=json.dumps({
                "old_password": old_password,
                "new_password": new_password
            }),
            content_type="application/json"
        )

    def login_client(self, username="", password=""):
        # get a token from DRF
        response = self.client.post(
            reverse("create-token"),
            data=json.dumps(
                {
                    'username': username,
                    'password': password
                }
            ),
            content_type='application/json'
        )
        self.token = response.data['token']
        # set the token in the header
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.token
        )
        self.client.login(username=username, password=password)
        return self.token

    def register_a_user(self, username="", password="", email=""):
        return self.client.post(
            reverse(
                "auth-register",
                kwargs={
                    "version": "v1"
                }
            ),
            data=json.dumps(
                {
                    "username": username,
                    "password": password,
                    "email": email
                }
            ),
            content_type='application/json'
        )

    def setUp(self):

        # create a admin user
        self.user = User.objects.create_superuser(
            username="test_user",
            email="test@mail.com",
            password="testing"
        )
        # add test data
        self.gunControl = self.create_debate("Gun control", "Should we ban assault rifles?")
        self.abortion = self.create_debate("Abortion", "Is it a woman's right to choose?")
        self.borderWall = self.create_debate("The border wall", "Is it an effective border security tool?")
        self.vetting = self.create_debate("Vetting", "Are we doing enough?")

        self.create_progress_point(self.user, self.gunControl, "Civilians can't own tanks though.")
        self.create_progress_point(self.user, self.abortion, "We allow parents to refuse to donate organs to their child.")
        self.create_progress_point(self.user, self.borderWall, "Drones cost 1/100th of the price.")

        self.starred_list = self.create_starred_list(self.user, self.gunControl)


        self.valid_progress_point_data = {
            "debate_pk": self.gunControl.pk,
            "debate_point": "Civilians can't own tanks though."
        }
        self.valid_progress_point_completed_data = {
            "debate_pk": self.gunControl.pk,
            "completed": True
        }
        self.invalid_progress_point_data_empty = {
            "debate_pk": "",
            "debate_point": ""
        }
        self.invalid_progress_point_completed_data_empty = {
            "debate_pk": "",
            "completed": ""
        }

        self.valid_starred_list_data = {
            "debate_pk": self.abortion.pk,
        }
        self.invalid_starred_list_data_empty = {
            "debate_pk": "",
        }
        self.invalid_starred_list_data = {
            "debate_pk": 100000000000,
        }

class ProgressModelTest(BaseViewTest):
    def test_basic_create_a_progress_point(self):
        """"
        This test ensures that the progress point created exists
        """
        progress_point = Progress.objects.get(user=self.user, debate=self.gunControl)

        self.assertEqual(progress_point.user.username, "test_user")
        self.assertEqual(progress_point.debate.title, "Gun control")
        self.assertEqual(progress_point.completed, False)
        self.assertEqual(progress_point.seen_points, ["Civilians can't own tanks though."])
        self.assertEqual(str(progress_point), "test_user - Gun control")

class DebateModelTest(BaseViewTest):
    def test_basic_create_a_debate(self):
        """"
        This test ensures that the debate created exists
        """
        debate = Debate.objects.create(
            title="Test debate",
            subtitle="test debate subtitle"
        )
        self.assertEqual(debate.title, "Test debate")
        self.assertEqual(debate.subtitle, "test debate subtitle")
        self.assertEqual(str(debate), "Test debate - test debate subtitle")

class StarredModelTest(BaseViewTest):
    def test_basic_create_a_starred_list(self):
        """"
        This test ensures that the reading list created exists
        """
        starred_list = Starred.objects.create(user=self.user)
        starred_list.starred_list.add(self.gunControl)
        self.assertTrue(starred_list.starred_list.filter(pk=self.gunControl.pk).exists())
        self.assertEqual(str(starred_list), "test_user - Gun control")

class GetAllDebatesTest(BaseViewTest):

    def test_get_all_debates(self):
        """
        This test ensures that all debate added in the setUp method
        exist when we make a GET request to the debate/ endpoint
        """
        # hit the API endpoint
        response = self.client.get(
            reverse("get-all-debates", kwargs={"version": "v1"})
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
        print(response)
        # fetch the data from db
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test with a debate that does not exist
        response = self.fetch_a_debate(100000000000)
        self.assertEqual(
            response.data["message"],
            "Debate with ID: 100000000000 does not exist"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class AddProgressPointTest(BaseViewTest):

    def test_create_a_progress_point(self):
        """
        This test ensures that a single progress point can be added
        """
        self.login_client('test_user', 'testing')
        # hit the API endpoint
        response = self.make_a_create_progress_request(
            kind="post",
            version="v1",
            data=self.valid_progress_point_data
        )
        self.assertEqual(response.data["seen_points"][-1], self.valid_progress_point_data["debate_point"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test with invalid data
        response = self.make_a_create_progress_request(
            kind="post",
            version="v1",
            data=self.invalid_progress_point_data_empty
        )
        self.assertEqual(
            response.data["message"],
            "Both debate ID and debate point are required to add a progress point"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class SetProgressPointCompletedTest(BaseViewTest):

    def test_set_progress_point_completed(self):
        """
        This test ensures that a single progress point can be set as completed
        """
        self.login_client('test_user', 'testing')
        # hit the API endpoint
        response = self.set_progress_point_completed_request(
            kind="post",
            version="v1",
            data=self.valid_progress_point_completed_data
        )
        self.assertTrue(response.data["completed"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test with invalid data
        response = self.set_progress_point_completed_request(
            kind="post",
            version="v1",
            data=self.invalid_progress_point_completed_data_empty
        )
        self.assertEqual(
            response.data["message"],
            "Both debate ID and completed status are required to update completed status"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetASingleProgressPointTest(BaseViewTest):

    def test_get_a_progress_point(self):
        """
        This test ensures that a single progress point of a given debate title is returned
        """
        valid_progress = Progress.objects.get(user=self.user, debate=self.gunControl)
        self.login_client('test_user', 'testing')
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
            response.data["message"],
            "Could not find debate with ID 10000000000"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # test with a progress point that does not exist
        response = self.fetch_progress_seen_points(self.vetting.pk)
        self.assertEqual(
            response.data["message"],
            "Could not retrieve progress"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class GetAllProgressPointsTest(BaseViewTest):

    def test_get_all_progress_points(self):
        """
        This test ensures that a all progress points can be returned
        """
        valid_progress = Progress.objects.filter(user=self.user)
        self.login_client('test_user', 'testing')
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
        self.login_client('test_user', 'testing')
        # hit the API endpoint
        response = self.make_a_create_starred_list_request(
            kind="post",
            version="v1",
            data=self.valid_starred_list_data
        )
        self.assertTrue(self.abortion.pk in response.data["starred_list"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test with invalid data
        response = self.make_a_create_starred_list_request(
            kind="post",
            version="v1",
            data=self.invalid_starred_list_data_empty
        )
        self.assertEqual(
            response.data["message"],
            "A debate ID is required"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # test with a debate that does not exist
        response = self.make_a_create_starred_list_request(
            kind="post",
            version="v1",
            data=self.invalid_starred_list_data
        )
        self.assertEqual(
            response.data["message"],
            "Could not find debate with ID 100000000000"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetASingleStarredTest(BaseViewTest):

    def test_get_a_starred_list(self):
        """
        This test ensures that a single progress point of a given debate title is returned
        """
        valid_starred_list = Starred.objects.get(user=self.user)
        self.login_client('test_user', 'testing')
        # hit the API endpoint
        response = self.fetch_starred_list()
        # fetch the data from db
        expected = Starred.objects.get(user=valid_starred_list.user)
        serialized = StarredSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class AuthChangePasswordTest(BaseViewTest):
    """
    Tests for the auth/change-password/ endpoint
    """

    def test_change_password(self):
        # test login with valid credentials
        self.login_client('test_user', 'testing')
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
    Tests for the auth/login/ endpoint
    """

    def test_login_user_with_valid_credentials(self):
        # test login with valid credentials
        response = self.login_a_user("test_user", "testing")
        # assert token key exists
        self.assertIn("token", response.data)
        # assert status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # refresh token
        response = self.refresh_token(response.data["token"])
        # assert token key exists
        self.assertIn("token", response.data)
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
        url = reverse(
            "auth-register",
            kwargs={
                "version": "v1"
            }
        )
        response = self.client.post(
            url,
            data=json.dumps(
                {
                    "username": "new_user",
                    "password": "new_pass",
                    "email": "new_user@mail.com"
                }
            ),
            content_type="application/json"
        )
        # assert status code is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_a_user_with_invalid_data(self):
        url = reverse(
            "auth-register",
            kwargs={
                "version": "v1"
            }
        )
        response = self.client.post(
            url,
            data=json.dumps(
                {
                    "username": "",
                    "password": "",
                    "email": ""
                }
            ),
            content_type='application/json'
        )
        # assert status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
