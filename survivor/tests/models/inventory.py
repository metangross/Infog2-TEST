from django.test.testcases import TestCase

from survivor.models import Inventory
from survivor.tests.factories.inventory import InventoryFactory


class InventoryTest(TestCase):
    def setUp(self):
        self.inventory = InventoryFactory()

    def test_create_from_factory(self):
        self.assertTrue(isinstance(self.inventory, Inventory))
        self.assertEqual(
            self.inventory.__str__(),
            f"{self.inventory.owner_survivor.name}'s inventory",
        )
