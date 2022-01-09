from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from survivor.models import Report
from survivor.serializers import ReportSerializer
from survivor.tests.factories.report import ReportFactory
from survivor.tests.factories.survivor import SurvivorFactory


class ReportViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_report_list(self):
        report = ReportFactory.create_batch(10)
        list_url = reverse("report-list")
        resp = self.client.get(list_url)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(len(report), len(data))
        for index in range(len(report)):
            self.assertEqual(report[index].id, data[index]["id"])
            self.assertEqual(report[index].gotReported.id, data[index]["gotReported"])
            self.assertEqual(report[index].whoReported.id, data[index]["whoReported"])

    def test_get_report(self):
        report = ReportFactory()
        detail_url = reverse("report-detail", kwargs={"pk": report.pk})
        resp = self.client.get(detail_url)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(report.id, data["id"])
        self.assertEqual(report.gotReported.id, data["gotReported"])
        self.assertEqual(report.whoReported.id, data["whoReported"])

    def test_post_report(self):
        survivor = SurvivorFactory(infected=False)
        survivor_2 = SurvivorFactory(infected=False)
        data = {"gotReported": survivor.id, "whoReported": survivor_2.id}
        post_url = reverse("report-list")
        resp = self.client.post(post_url, data, format="json")
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(status.HTTP_201_CREATED, resp.status_code)
        data = resp.json()
        instance = Report.objects.last()
        instance = ReportSerializer(instance=instance).data
        self.assertEqual(data, instance)

    def test_post_infected_report(self):
        survivor = SurvivorFactory(infected=False)
        survivor_2 = SurvivorFactory(infected=True)
        data = {"gotReported": survivor.id, "whoReported": survivor_2.id}
        post_url = reverse("report-list")
        resp = self.client.post(post_url, data, format="json")
        self.assertTrue(status.is_client_error(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_report_thrice(self):
        survivor = SurvivorFactory.create_batch(4, infected=False)
        for index in range(3):
            data = {"gotReported": survivor[3].id, "whoReported": survivor[index].id}
            post_url = reverse("report-list")
            resp = self.client.post(post_url, data, format="json")
            self.assertTrue(status.is_success(resp.status_code))
            self.assertEqual(status.HTTP_201_CREATED, resp.status_code)
            self.assertEqual(False, survivor[index].infected)
        survivor[3].refresh_from_db()
        self.assertEqual(True, survivor[3].infected)

    def test_post_report_himself(self):
        survivor = SurvivorFactory()
        data = {"gotReported": survivor.id, "whoReported": survivor.id}
        post_url = reverse("report-list")
        resp = self.client.post(post_url, data, format="json")
        self.assertTrue(status.is_client_error(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_report_invalid(self):
        data = {"gotReported": 1, "whoReported": 3}
        post_url = reverse("report-list")
        resp = self.client.post(post_url, data, format="json")
        self.assertTrue(status.is_client_error(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
