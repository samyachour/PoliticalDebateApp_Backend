from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from rest_api.models import Debates
from .serializers import DebatesSerializer

# tests for views


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_debate(title="", subtitle=""):
        if title != "" and subtitle != "":
            Debates.objects.create(title=title, subtitle=subtitle)

    def setUp(self):
        # add test data
        self.create_debate("Gun control", "assault rifle ban")
        self.create_debate("Obamacare", "is it working")
        self.create_debate("Climate change", "is it man-made")


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
