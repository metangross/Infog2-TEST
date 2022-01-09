from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from survivor.tests.factories.inventory import InventoryFactory


class InventoryViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_inventory_list(self):
        inventory = InventoryFactory.create_batch(10, owner_survivor__infected=False)
        list_url = reverse("inventory-list")
        resp = self.client.get(list_url)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(len(inventory), len(data))
        for index in range(len(inventory)):
            self.assertEqual(inventory[index].id, data[index]["id"])
            self.assertEqual(inventory[index].water, data[index]["water"])
            self.assertEqual(inventory[index].food, data[index]["food"])
            self.assertEqual(inventory[index].meds, data[index]["meds"])
            self.assertEqual(inventory[index].ammo, data[index]["ammo"])
            self.assertEqual(
                inventory[index].owner_survivor.id, data[index]["owner_survivor"]
            )

    def test_get_inventory(self):
        inventory = InventoryFactory(owner_survivor__infected=False)
        detail_url = reverse("inventory-detail", kwargs={"pk": inventory.pk})
        resp = self.client.get(detail_url)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(inventory.id, data["id"])
        self.assertEqual(inventory.water, data["water"])
        self.assertEqual(inventory.food, data["food"])
        self.assertEqual(inventory.meds, data["meds"])
        self.assertEqual(inventory.ammo, data["ammo"])
        self.assertEqual(inventory.owner_survivor.id, data["owner_survivor"])

    def test_get_infected_inventory(self):
        inventory = InventoryFactory(owner_survivor__infected=True)
        detail_url = reverse("inventory-detail", kwargs={"pk": inventory.pk})
        resp = self.client.get(detail_url)
        self.assertTrue(status.is_client_error(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
