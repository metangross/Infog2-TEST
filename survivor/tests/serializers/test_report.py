from django.test.testcases import TestCase
from rest_framework.exceptions import ValidationError

from survivor.models import Report
from survivor.serializers import ReportSerializer
from survivor.tests.factories.report import ReportFactory
from survivor.tests.factories.survivor import SurvivorFactory


class ReportSerializerTest(TestCase):
    def setUp(self):
        self.report = ReportFactory()
        self.survivor = SurvivorFactory(infected=False)
        self.survivor_2 = SurvivorFactory(infected=False)
        self.data = {"gotReported": self.survivor.id, "whoReported": self.survivor_2.id}

    def test_create_report(self):
        serializer = ReportSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        report = serializer.save()
        self.assertEqual(report.gotReported.id, serializer.data["gotReported"])
        self.assertEqual(report.whoReported.id, serializer.data["whoReported"])

    def test_report_invalid(self):
        self.data["gotReported"] = "eae"
        serializer = ReportSerializer(data=self.data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()
            self.assertEquals(Report.objects.count(), 1)

    def test_serialize_report(self):
        data = ReportSerializer(self.report).data
        self.assertEqual(self.report.gotReported.id, data["gotReported"])
        self.assertEqual(self.report.whoReported.id, data["whoReported"])
