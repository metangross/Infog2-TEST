from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from survivor.models import Inventory, Report, Survivor


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"


class InventoryCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        exclude = ["id", "owner_survivor"]


class SurvivorSerializer(serializers.ModelSerializer):
    inventory = InventoryCreatorSerializer()

    class Meta:
        model = Survivor
        fields = [
            "id",
            "name",
            "age",
            "gender",
            "longitude",
            "latitude",
            "infected",
            "inventory",
        ]
        read_only_fields = ["infected"]

    def create(self, validated_data):
        inv = validated_data.pop("inventory")
        survivor = Survivor.objects.create(**validated_data)
        Inventory.objects.create(owner_survivor=survivor, **inv)
        return survivor


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survivor
        fields = ["latitude", "longitude"]


class TradeSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Survivor.objects.all())
    trd_water = serializers.IntegerField(min_value=0)
    trd_food = serializers.IntegerField(min_value=0)
    trd_meds = serializers.IntegerField(min_value=0)
    trd_ammo = serializers.IntegerField(min_value=0)


class ExchangeSerializer(serializers.Serializer):
    trader_1 = TradeSerializer()
    trader_2 = TradeSerializer()


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"

    def validate(self, attrs):
        reported = attrs["gotReported"]
        reporter = attrs["whoReported"]
        if reported == reporter:
            raise ValidationError({"error": "Survivor can't report itself"})
        return super().validate(attrs)

    def validate_whoReported(self, value):
        if value.infected:
            raise ValidationError({"error": "Infected Survivor can't report"})
        return value

    def create(self, validated_data):
        instance = super().create(validated_data)
        reported = validated_data["gotReported"]
        if not reported.infected and reported.reported.count() >= 3:
            reported.infected = True
            reported.save(update_fields=["infected"])
        return instance


class RecordSerializer(serializers.Serializer):
    infected_percent = serializers.DecimalField(
        max_digits=6, decimal_places=3, min_value=0
    )
    survivors_percent = serializers.DecimalField(
        max_digits=6, decimal_places=3, min_value=0
    )
    avg_water = serializers.DecimalField(max_digits=5, decimal_places=3, min_value=0)
    avg_food = serializers.DecimalField(max_digits=5, decimal_places=3, min_value=0)
    avg_meds = serializers.DecimalField(max_digits=5, decimal_places=3, min_value=0)
    avg_ammo = serializers.DecimalField(max_digits=5, decimal_places=3, min_value=0)
    lostpt = serializers.FloatField(min_value=0)
