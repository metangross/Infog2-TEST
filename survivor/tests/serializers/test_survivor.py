from django.test.testcases import TestCase
from rest_framework.exceptions import ValidationError

from survivor.choices import FEMALE
from survivor.models import Survivor
from survivor.serializers import SurvivorSerializer
from survivor.tests.factories.survivor import SurvivorFactory


class SurvivorSerializerTest(TestCase):
    def setUp(self):
        self.data = {
            "name": "Teste",
            "age": 25,
            "gender": FEMALE,
            "latitude": 50,
            "longitude": 50,
            "inventory": {"water": 40, "food": 4, "meds": 3, "ammo": 2},
        }
        self.survivor = SurvivorFactory(infected=False)

    def test_create_survivor(self):
        serializer = SurvivorSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        survivor = serializer.save()
        self.assertEqual(survivor.name, serializer.data["name"])
        self.assertEqual(survivor.age, serializer.data["age"])
        self.assertEqual(survivor.gender, serializer.data["gender"])
        self.assertEqual(survivor.latitude, serializer.data["latitude"])
        self.assertEqual(survivor.longitude, serializer.data["longitude"])
        self.assertFalse(survivor.infected)
        self.assertEqual(
            survivor.inventory.water, serializer.data["inventory"]["water"]
        )
        self.assertEqual(survivor.inventory.food, serializer.data["inventory"]["food"])
        self.assertEqual(survivor.inventory.meds, serializer.data["inventory"]["meds"])
        self.assertEqual(survivor.inventory.ammo, serializer.data["inventory"]["ammo"])

    def test_save_survivor_invalid(self):
        self.data["age"] = -50
        serializer = SurvivorSerializer(data=self.data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()
            self.assertEquals(Survivor.objects.count(), 1)

    def test_serialize_survivor(self):
        data = SurvivorSerializer(self.survivor).data
        self.assertEqual(self.survivor.name, data["name"])
        self.assertEqual(self.survivor.age, data["age"])
        self.assertEqual(self.survivor.gender, data["gender"])
        self.assertEqual(self.survivor.latitude, data["latitude"])
        self.assertEqual(self.survivor.longitude, data["longitude"])
        self.assertFalse(data["infected"])
        self.assertEqual(data["inventory"], None)
