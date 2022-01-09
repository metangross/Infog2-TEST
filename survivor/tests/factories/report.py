import factory
from faker import Faker

from survivor.models import Report
from survivor.tests.factories.survivor import SurvivorFactory

fake = Faker()


class ReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Report

    gotReported = factory.SubFactory(SurvivorFactory)
    whoReported = factory.SubFactory(SurvivorFactory)
