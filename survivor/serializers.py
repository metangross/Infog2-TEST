from django.db.models import query
from django.db.models.fields import Field
from rest_framework.response import Response
from survivor.models import Survivor, Inventory, Report
from rest_framework import serializers

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"


class SurvivorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Survivor
        fields = "__all__"
        read_only_fields = ["infected"]

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survivor
        fields = ["latitude", "longitude"]

class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        fields = "__all__"
    

    def save(self, **kwargs):

        super().save(**kwargs)
        survivor = self.validated_data['gotReported']
        reporter = self.validated_data['whoReported']
        report_count = Report.objects.filter(gotReported=survivor).count()
        if report_count >= 3 and survivor.infected is False:
            survivor.infected = True
            survivor.save(update_fields=['infected'])
            return Response({

            })
            