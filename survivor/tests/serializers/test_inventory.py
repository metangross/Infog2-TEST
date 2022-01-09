from django.test.testcases import TestCase
from rest_framework.exceptions import ValidationError

from survivor.models import Inventory
from survivor.serializers import InventorySerializer
from survivor.tests.factories.inventory import InventoryFactory
from survivor.tests.factories.survivor import SurvivorFactory


class InventorySerializerTest(TestCase):
    def setUp(self):
        self.survivor = SurvivorFactory()
        self.inventory = InventoryFactory()
        self.data = {
            "owner_survivor": self.survivor.id,
            "water": 5,
            "food": 4,
            "meds": 3,
            "ammo": 2,
        }

    def test_create_inventory(self):
        serializer = InventorySerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        inventory = serializer.save()
        self.assertEqual(inventory.owner_survivor.id, serializer.data["owner_survivor"])
        self.assertEqual(inventory.water, serializer.data["water"])
        self.assertEqual(inventory.food, serializer.data["food"])
        self.assertEqual(inventory.meds, serializer.data["meds"])
        self.assertEqual(inventory.ammo, serializer.data["ammo"])

    def test_inventory_invalid(self):
        self.data["water"] = -9
        serializer = InventorySerializer(data=self.data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()
            self.assertEquals(Inventory.objects.count(), 1)

    def test_serialize_inventory(self):
        data = InventorySerializer(self.inventory).data
        self.assertEqual(self.inventory.owner_survivor.id, data["owner_survivor"])
        self.assertEqual(self.inventory.water, data["water"])
        self.assertEqual(self.inventory.food, data["food"])
        self.assertEqual(self.inventory.meds, data["meds"])
        self.assertEqual(self.inventory.ammo, data["ammo"])
