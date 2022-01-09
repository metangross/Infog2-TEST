from django.test.testcases import TestCase

from survivor.models import Survivor
from survivor.tests.factories.survivor import SurvivorFactory


class SurvivorTest(TestCase):
    def setUp(self):
        self.survivor = SurvivorFactory()

    def test_create_from_factory(self):
        self.assertTrue(isinstance(self.survivor, Survivor))
        self.assertEqual(self.survivor.__str__(), self.survivor.name)
