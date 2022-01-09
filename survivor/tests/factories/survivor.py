from random import choice

import factory
from faker import Faker

from survivor.choices import GENDER_CHOICES
from survivor.models import Survivor

fake = Faker()


class SurvivorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Survivor

    name = factory.LazyFunction(lambda: fake.name())
    age = factory.LazyFunction(lambda: fake.pyint(min_value=0))
    gender = choice(GENDER_CHOICES)[0]
    latitude = factory.LazyFunction(lambda: fake.pyfloat(min_value=-90, max_value=90))
    longitude = factory.LazyFunction(
        lambda: fake.pyfloat(min_value=-180, max_value=180)
    )
    infected = factory.LazyFunction(lambda: fake.pybool())
