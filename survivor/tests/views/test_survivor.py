from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from survivor.choices import FEMALE
from survivor.models import Survivor
from survivor.tests.factories.inventory import InventoryFactory
from survivor.tests.factories.survivor import SurvivorFactory


class SurvivorViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("survivor-list")
        self.data = {
            "name": "Teste",
            "age": 25,
            "gender": FEMALE,
            "latitude": 50,
            "longitude": 50,
            "inventory": {"water": 40, "food": 4, "meds": 3, "ammo": 2},
        }

    def test_get_survivor_list(self):
        survivors = SurvivorFactory.create_batch(10, infected=False)
        resp = self.client.get(self.list_url)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(len(survivors), len(data))
        for index in range(len(survivors)):
            self.assertEqual(survivors[index].name, data[index]["name"])
            self.assertEqual(survivors[index].age, data[index]["age"])
            self.assertEqual(survivors[index].gender, data[index]["gender"])
            self.assertEqual(survivors[index].latitude, data[index]["latitude"])
            self.assertEqual(survivors[index].longitude, data[index]["longitude"])
            self.assertEqual(survivors[index].infected, data[index]["infected"])
            self.assertEqual(data[index]["inventory"], None)

    def test_get_survivor(self):
        survivor = SurvivorFactory(infected=False)
        detail_url = reverse("survivor-detail", kwargs={"pk": survivor.pk})
        resp = self.client.get(detail_url)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(survivor.name, data["name"])
        self.assertEqual(survivor.age, data["age"])
        self.assertEqual(survivor.gender, data["gender"])
        self.assertEqual(survivor.latitude, data["latitude"])
        self.assertEqual(survivor.longitude, data["longitude"])
        self.assertEqual(survivor.infected, data["infected"])
        self.assertEqual(data["inventory"], None)

    def test_get_infected_survivor(self):
        survivor = SurvivorFactory(infected=True)
        detail_url = reverse("survivor-detail", kwargs={"pk": survivor.pk})
        resp = self.client.get(detail_url)
        self.assertTrue(status.is_client_error(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_survivor(self):
        post_url = reverse("survivor-list")
        resp = self.client.post(post_url, self.data, format="json")
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(status.HTTP_201_CREATED, resp.status_code)
        data = resp.json()
        self.assertEqual(self.data["name"], data["name"])
        self.assertEqual(self.data["age"], data["age"])
        self.assertEqual(self.data["gender"], data["gender"])
        self.assertEqual(self.data["latitude"], data["latitude"])
        self.assertEqual(self.data["longitude"], data["longitude"])
        self.assertEqual(False, data["infected"])
        self.assertEqual(self.data["inventory"]["water"], data["inventory"]["water"])
        self.assertEqual(self.data["inventory"]["food"], data["inventory"]["food"])
        self.assertEqual(self.data["inventory"]["meds"], data["inventory"]["meds"])
        self.assertEqual(self.data["inventory"]["ammo"], data["inventory"]["ammo"])
        self.assertEqual(Survivor.objects.count(), 1)

    def test_patch_survivor(self):
        survivor = SurvivorFactory(longitude=30, latitude=30, infected=False)
        patch = {"longitude": 45, "latitude": 50}
        patch_url = reverse("survivor-detail", kwargs={"pk": survivor.pk})
        resp = self.client.patch(patch_url, patch, format="json")
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(status.HTTP_200_OK, resp.status_code)
        data = resp.json()
        self.assertNotEqual(survivor.latitude, data["latitude"])
        self.assertNotEqual(survivor.longitude, data["longitude"])

    def test_patch_infected_survivor(self):
        survivor = SurvivorFactory(longitude=30, latitude=30, infected=True)
        patch = {"longitude": 45, "latitude": 50}
        patch_url = reverse("survivor-detail", kwargs={"pk": survivor.pk})
        resp = self.client.patch(patch_url, patch, format="json")
        self.assertTrue(status.is_client_error(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_trade_survivor(self):

        inventory_1 = InventoryFactory(
            owner_survivor__infected=False, water=5, food=5, meds=5, ammo=5
        )
        inventory_2 = InventoryFactory(
            owner_survivor__infected=False, water=5, food=5, meds=5, ammo=5
        )
        trade_data = {
            "trader_1": {
                "id": inventory_1.owner_survivor.id,
                "trd_water": 3,
                "trd_food": 1,
                "trd_meds": 3,
                "trd_ammo": 1,
            },
            "trader_2": {
                "id": inventory_2.owner_survivor.id,
                "trd_water": 1,
                "trd_food": 4,
                "trd_meds": 1,
                "trd_ammo": 4,
            },
        }
        post_url = reverse("survivor-trade")
        resp = self.client.post(post_url, trade_data, format="json")
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(status.HTTP_200_OK, resp.status_code)
        data = resp.json()
        self.assertEqual(data[0]["owner_survivor"], inventory_1.owner_survivor.id)
        self.assertEqual(data[0]["id"], inventory_1.id)
        self.assertEqual(
            data[0]["water"],
            inventory_1.water
            - trade_data["trader_1"]["trd_water"]
            + trade_data["trader_2"]["trd_water"],
        )
        self.assertEqual(
            data[0]["food"],
            inventory_1.food
            - trade_data["trader_1"]["trd_food"]
            + trade_data["trader_2"]["trd_food"],
        )
        self.assertEqual(
            data[0]["meds"],
            inventory_1.meds
            - trade_data["trader_1"]["trd_meds"]
            + trade_data["trader_2"]["trd_meds"],
        )
        self.assertEqual(
            data[0]["ammo"],
            inventory_1.ammo
            - trade_data["trader_1"]["trd_ammo"]
            + trade_data["trader_2"]["trd_ammo"],
        )
        self.assertEqual(data[1]["owner_survivor"], inventory_2.owner_survivor.id)
        self.assertEqual(data[1]["id"], inventory_2.id)
        self.assertEqual(
            data[1]["water"],
            inventory_2.water
            - trade_data["trader_2"]["trd_water"]
            + trade_data["trader_1"]["trd_water"],
        )
        self.assertEqual(
            data[1]["food"],
            inventory_2.food
            - trade_data["trader_2"]["trd_food"]
            + trade_data["trader_1"]["trd_food"],
        )
        self.assertEqual(
            data[1]["meds"],
            inventory_2.meds
            - trade_data["trader_2"]["trd_meds"]
            + trade_data["trader_1"]["trd_meds"],
        )
        self.assertEqual(
            data[1]["ammo"],
            inventory_2.ammo
            - trade_data["trader_2"]["trd_ammo"]
            + trade_data["trader_1"]["trd_ammo"],
        )

    def test_trade_infected_survivor(self):
        inventory_1 = InventoryFactory(
            owner_survivor__infected=True, water=5, food=5, meds=5, ammo=5
        )
        inventory_2 = InventoryFactory(
            owner_survivor__infected=False, water=5, food=5, meds=5, ammo=5
        )
        trade_data = {
            "trader_1": {
                "id": inventory_1.owner_survivor.id,
                "trd_water": 3,
                "trd_food": 1,
                "trd_meds": 3,
                "trd_ammo": 1,
            },
            "trader_2": {
                "id": inventory_2.owner_survivor.id,
                "trd_water": 1,
                "trd_food": 4,
                "trd_meds": 1,
                "trd_ammo": 4,
            },
        }
        post_url = reverse("survivor-trade")
        resp = self.client.post(post_url, trade_data, format="json")
        self.assertTrue(status.is_client_error(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_trade_different_points(self):
        inventory_1 = InventoryFactory(
            owner_survivor__infected=False, water=5, food=5, meds=5, ammo=5
        )
        inventory_2 = InventoryFactory(
            owner_survivor__infected=False, water=5, food=5, meds=5, ammo=5
        )
        trade_data = {
            "trader_1": {
                "id": inventory_1.owner_survivor.id,
                "trd_water": 2,
                "trd_food": 1,
                "trd_meds": 3,
                "trd_ammo": 1,
            },
            "trader_2": {
                "id": inventory_2.owner_survivor.id,
                "trd_water": 1,
                "trd_food": 4,
                "trd_meds": 1,
                "trd_ammo": 4,
            },
        }
        post_url = reverse("survivor-trade")
        resp = self.client.post(post_url, trade_data, format="json")
        self.assertTrue(status.is_client_error(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_trade_not_enough_inventory(self):
        inventory_1 = InventoryFactory(
            owner_survivor__infected=False, water=5, food=5, meds=5, ammo=5
        )
        inventory_2 = InventoryFactory(
            owner_survivor__infected=False, water=5, food=2, meds=5, ammo=5
        )
        trade_data = {
            "trader_1": {
                "id": inventory_1.owner_survivor.id,
                "trd_water": 3,
                "trd_food": 1,
                "trd_meds": 3,
                "trd_ammo": 1,
            },
            "trader_2": {
                "id": inventory_2.owner_survivor.id,
                "trd_water": 1,
                "trd_food": 4,
                "trd_meds": 1,
                "trd_ammo": 4,
            },
        }
        post_url = reverse("survivor-trade")
        resp = self.client.post(post_url, trade_data, format="json")
        self.assertTrue(status.is_client_error(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_trade_same_survivor(self):
        inventory_1 = InventoryFactory(
            owner_survivor__infected=False, water=5, food=5, meds=5, ammo=5
        )
        trade_data = {
            "trader_1": {
                "id": inventory_1.owner_survivor.id,
                "trd_water": 3,
                "trd_food": 1,
                "trd_meds": 3,
                "trd_ammo": 1,
            },
            "trader_2": {
                "id": inventory_1.owner_survivor.id,
                "trd_water": 1,
                "trd_food": 4,
                "trd_meds": 1,
                "trd_ammo": 4,
            },
        }
        post_url = reverse("survivor-trade")
        resp = self.client.post(post_url, trade_data, format="json")
        self.assertTrue(status.is_client_error(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_trade_invalid(self):
        trade_data = {
            "trader_1": {
                "id": 1,
                "trd_water": 3,
                "trd_food": 1,
                "trd_meds": 3,
                "trd_ammo": 1,
            },
            "trader_2": {
                "id": 2,
                "trd_water": 1,
                "trd_food": 4,
                "trd_meds": 1,
                "trd_ammo": 4,
            },
        }
        post_url = reverse("survivor-trade")
        resp = self.client.post(post_url, trade_data, format="json")
        self.assertTrue(status.is_client_error(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_report(self):
        inventories = InventoryFactory.create_batch(
            10, owner_survivor__infected=False, water=10, food=10, meds=10, ammo=10
        )
        inventory = InventoryFactory(
            owner_survivor__infected=True, water=5, food=5, meds=5, ammo=5
        )
        record_url = reverse("survivor-record")

        resp = self.client.get(record_url)
        data = resp.json()
        total_water = 0
        total_food = 0
        total_meds = 0
        total_ammo = 0
        for i in inventories:
            total_water += i.water
            total_food += i.food
            total_meds += i.meds
            total_ammo += i.ammo
        infected_percent = round(1 / (len(inventories) + 1) * 100, 3)
        survivors_percent = round(len(inventories) / (len(inventories) + 1) * 100, 3)
        avg_water = round((total_water + inventory.water) / (len(inventories) + 1), 3)
        avg_food = round((total_food + inventory.food) / (len(inventories) + 1), 3)
        avg_meds = round((total_meds + inventory.meds) / (len(inventories) + 1), 3)
        avg_ammo = round((total_ammo + inventory.ammo) / (len(inventories) + 1), 3)
        lostpt = (
            inventory.water * 4
            + inventory.food * 3
            + inventory.meds * 2
            + inventory.ammo * 1 / 1.0
        )
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data["infected_percent"], str(infected_percent))
        self.assertEqual(data["survivors_percent"], str(survivors_percent))
        self.assertEqual(data["avg_water"], str(avg_water))
        self.assertEqual(data["avg_food"], str(avg_food))
        self.assertEqual(data["avg_meds"], str(avg_meds))
        self.assertEqual(data["avg_ammo"], str(avg_ammo))
        self.assertEqual(data["lostpt"], lostpt)
