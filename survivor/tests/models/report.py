from django.test.testcases import TestCase

from survivor.models import Report
from survivor.tests.factories.report import ReportFactory


class ReportTest(TestCase):
    def setUp(self):
        self.report = ReportFactory()

    def test_create_report(self):
        self.assertTrue(isinstance(self.report, Report))
        self.assertEqual(
            self.report.__str__(),
            f"{self.report.gotReported} reported by {self.report.whoReported}",
        )
