from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from .models import Debates
from .serializers import DebatesSerializer

# tests for views


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_debate(title="", subtitle=""):
        if title != "" and subtitle != "":
            debates.objects.create(title=title, subtitle=subtitle)

    def setUp(self):
        # add test data
        self.create_debate("Gun control", "Banning assault rifles")
        self.create_debate("Abortion", "A woman's right to choose")
        self.create_debate("Obamacare", "Is it helping people (on the whole)")


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
