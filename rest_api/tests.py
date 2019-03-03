from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from rest_api.models import Debates, Progress
from .serializers import *
import json

# tests for views

class ProgressModelTest(APITestCase):
    def setUp(self):
        self.progress_point = Progress.objects.create(
            user_ID="1234",
            debate_title="Gun control",
            debate_point="Civilians can't own tanks though."
        )

    def test_song(self):
        """"
        This test ensures that the progress point created in the setup
        exists
        """
        self.assertEqual(self.progress_point.user_ID, "1234")
        self.assertEqual(self.progress_point.debate_title, "Gun control")
        self.assertEqual(self.progress_point.debate_point, "Civilians can't own tanks though.")
        self.assertEqual(str(self.progress_point), "1234 - Gun control - Civilians can't own tanks though.")

class DebatesModelTest(APITestCase):
    def setUp(self):
        self.debate = Debates.objects.create(
            title="Gun control",
            subtitle="Should we ban assault rifles?"
        )

    def test_song(self):
        """"
        This test ensures that the debate created in the setup
        exists
        """
        self.assertEqual(self.debate.title, "Gun control")
        self.assertEqual(self.debate.subtitle, "Should we ban assault rifles?")
        self.assertEqual(str(self.debate), "Gun control - Should we ban assault rifles?")

class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_debate(title="", subtitle=""):
        if title != "" and subtitle != "":
            Debates.objects.create(title=title, subtitle=subtitle)

    @staticmethod
    def create_progress_point(user_ID="", debate_title="", debate_point=""):
        if user_ID != "" and debate_title != "" and debate_point != "":
            Progress.objects.create(user_ID=user_ID, debate_title=debate_title, debate_point=debate_point)

    def make_a_request(self, kind="post", **kwargs):
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

    def fetch_a_debate(self, pk=0):
        return self.client.get(
            reverse(
                "get-debate",
                kwargs={
                    "version": "v1",
                    "pk": pk
                }
            )
        )

    def fetch_a_progress_point(self, pk=0):
        return self.client.get(
            reverse(
                "get-progress",
                kwargs={
                    "version": "v1",
                    "pk": pk
                }
            )
        )

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
            password="testing",
            first_name="test",
            last_name="user",
        )
        # add test data
        self.create_debate("Gun control", "Should we ban assault rifles?")
        self.create_debate("Abortion", "Is it a woman's right to choose?")
        self.create_debate("The border wall", "Is it an effective border security tool?")

        self.create_progress_point("1234", "Gun control", "Civilians can't own tanks though.")
        self.create_progress_point("1234", "Abortion", "We allow parents to refuse to donate organs to their child.")
        self.create_progress_point("1234", "The border wall", "Drones cost 1/100th of the price.")

        self.valid_progress_point_data = {
            "debate_title": "test debate title",
            "debate_point": "test debate point"
        }
        self.invalid_progress_point_data = {
            "debate_title": "",
            "debate_point": ""
        }

        self.valid_debate_id = 14
        self.valid_progress_point_id = 17
        self.invalid_id = 1000000000

class GetAllDebatesTest(BaseViewTest):

    def test_get_all_debates(self):
        """
        This test ensures that all debates added in the setUp method
        exist when we make a GET request to the debates/ endpoint
        """
        # hit the API endpoint
        response = self.client.get(
            reverse("debates-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = Debates.objects.all()
        serialized = DebatesSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetASingleDebateTest(BaseViewTest):

    def test_get_a_debate(self):
        """
        This test ensures that a single debate of a given id is
        returned
        """
        valid_id = Debates.objects.get(title="Gun control").id
        # hit the API endpoint
        response = self.fetch_a_debate(valid_id)
        # fetch the data from db
        expected = Debates.objects.get(pk=valid_id)
        serialized = DebatesSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test with a song that does not exist
        response = self.fetch_a_debate(self.invalid_id)
        self.assertEqual(
            response.data["message"],
            "Debate with id: 1000000000 does not exist"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class AddProgressPointTest(BaseViewTest):

    def test_create_a_progress_point(self):
        """
        This test ensures that a single progress point can be added
        """
        self.login_client('test_user', 'testing')
        # hit the API endpoint
        response = self.make_a_request(
            kind="post",
            version="v1",
            data=self.valid_progress_point_data
        )
        self.assertEqual(response.data, self.valid_progress_point_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test with invalid data
        response = self.make_a_request(
            kind="post",
            version="v1",
            data=self.invalid_progress_point_data
        )
        self.assertEqual(
            response.data["message"],
            "Both debate title and debate point are required to add a progress point"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetASingleProgressPointTest(BaseViewTest):

    def test_get_a_progress_point(self):
        """
        This test ensures that a single progress point of a given id is
        returned
        """
        valid_id = Progress.objects.get(debate_title="Gun control").id
        self.login_client('test_user', 'testing')
        # hit the API endpoint
        response = self.fetch_a_progress_point(valid_id)
        # fetch the data from db
        expected = Progress.objects.get(pk=valid_id)
        serialized = ProgressSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test with a song that does not exist
        response = self.fetch_a_progress_point(self.invalid_id)
        self.assertEqual(
            response.data["message"],
            "Could not retrieve progress"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
