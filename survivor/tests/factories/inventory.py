import factory
from faker import Faker

from survivor.models import Inventory
from survivor.tests.factories.survivor import SurvivorFactory

fake = Faker()


class InventoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Inventory

    owner_survivor = factory.SubFactory(SurvivorFactory)
    water = factory.LazyFunction(lambda: fake.pyint(min_value=0))
    food = factory.LazyFunction(lambda: fake.pyint(min_value=0))
    meds = factory.LazyFunction(lambda: fake.pyint(min_value=0))
    ammo = factory.LazyFunction(lambda: fake.pyint(min_value=0))
