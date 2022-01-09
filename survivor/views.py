from decouple import config
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Inventory, Report, Survivor
from .serializers import (
    ExchangeSerializer,
    InventoryCreatorSerializer,
    InventorySerializer,
    LocationSerializer,
    RecordSerializer,
    ReportSerializer,
    SurvivorSerializer,
)

# Create your views here.

PTS_WATER = int(config("PTS_WATER"))
PTS_FOOD = int(config("PTS_FOOD"))
PTS_MEDS = int(config("PTS_MEDS"))
PTS_AMMO = int(config("PTS_AMMO"))


class SurvivorViewSet(viewsets.ModelViewSet):

    queryset = Survivor.objects.all()
    serializer_class = SurvivorSerializer
    # POST /Survivor/trade
    @action(methods=["post"], detail=False)
    def trade(self, request):
        serializer = ExchangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trader_1 = serializer.data["trader_1"]
        trader_2 = serializer.data["trader_2"]
        if trader_1["id"] == trader_2["id"]:
            return Response(
                {"error": "Trade must be between different survivors"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        trader_1_survivor = get_object_or_404(Survivor, pk=trader_1["id"])
        trader_2_survivor = get_object_or_404(Survivor, pk=trader_2["id"])
        if trader_1_survivor.infected or trader_2_survivor.infected:
            return Response(
                {"error": "One of the trading parties is infected"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        points_1 = (
            trader_1["trd_water"] * PTS_WATER
            + trader_1["trd_food"] * PTS_FOOD
            + trader_1["trd_meds"] * PTS_MEDS
            + trader_1["trd_ammo"] * PTS_AMMO
        )
        points_2 = (
            trader_2["trd_water"] * PTS_WATER
            + trader_2["trd_food"] * PTS_FOOD
            + trader_2["trd_meds"] * PTS_MEDS
            + trader_2["trd_ammo"] * PTS_AMMO
        )
        if points_1 != points_2:
            return Response(
                {"error": "Both parties must trade an equal ammount of points"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trader_1_inventory = get_object_or_404(
            Inventory, owner_survivor=trader_1_survivor
        )
        trader_2_inventory = get_object_or_404(
            Inventory, owner_survivor=trader_2_survivor
        )

        trader_1_serialize = InventoryCreatorSerializer(instance=trader_1_inventory)
        trader_1_data = trader_1_serialize.data
        trader_2_serialize = InventoryCreatorSerializer(instance=trader_2_inventory)
        trader_2_data = trader_2_serialize.data
        for attr in trader_1_data:
            if attr != "id" and attr != "owner_survivor":
                trader_1_data[attr] += trader_2[f"trd_{attr}"] - trader_1[f"trd_{attr}"]
                trader_2_data[attr] += trader_1[f"trd_{attr}"] - trader_2[f"trd_{attr}"]
        trader_1_serialize = InventoryCreatorSerializer(
            instance=trader_1_inventory, data=trader_1_data
        )
        trader_2_serialize = InventoryCreatorSerializer(
            instance=trader_2_inventory, data=trader_2_data
        )
        with transaction.atomic():
            trader_1_serialize.is_valid(raise_exception=True)
            trader_2_serialize.is_valid(raise_exception=True)
            trader_1_serialize.save()
            trader_2_serialize.save()
        response = [
            InventorySerializer(trader_1_inventory).data,
            InventorySerializer(trader_2_inventory).data,
        ]
        return Response(response, status=status.HTTP_200_OK)

    # GET /Survivor/report
    @action(methods=["get"], detail=False)
    def record(self, request):
        infected = Survivor.objects.filter(infected=True).count()
        survivors_count = Survivor.objects.filter(infected=False).count()
        total = infected + survivors_count
        if survivors_count == 0:
            return Response(
                {"error": "No survivors"}, status=status.HTTP_400_BAD_REQUEST
            )
        infected_percent = (infected / total) * 100
        survivors_percent = 100 - infected_percent
        water = 0
        food = 0
        meds = 0
        ammo = 0
        survivors = Survivor.objects.all()
        for survivor in survivors:
            water += survivor.inventory.water
            food += survivor.inventory.food
            meds += survivor.inventory.meds
            ammo += survivor.inventory.ammo
        avg_water = water / total
        avg_food = food / total
        avg_meds = meds / total
        avg_ammo = ammo / total
        infected_survivors = Survivor.objects.filter(infected=True)
        lostpt = 0
        for iftd in infected_survivors:
            lostpt += iftd.inventory.water * PTS_WATER
            lostpt += iftd.inventory.food * PTS_FOOD
            lostpt += iftd.inventory.meds * PTS_MEDS
            lostpt += iftd.inventory.ammo * PTS_AMMO
        serializer = RecordSerializer(
            {
                "infected_percent": infected_percent,
                "survivors_percent": survivors_percent,
                "avg_water": avg_water,
                "avg_food": avg_food,
                "avg_meds": avg_meds,
                "avg_ammo": avg_ammo,
                "lostpt": lostpt,
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        survivor = get_object_or_404(Survivor, pk=pk)
        if survivor.infected:
            return Response(
                {"error": "Selected survivor is infected"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        survivor = get_object_or_404(Survivor, pk=pk)
        if not survivor.infected:
            serializer = LocationSerializer(survivor, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_serializer = SurvivorSerializer(survivor)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Selected survivor is infected"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class InventoryViewSet(viewsets.ModelViewSet):

    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        inventory = get_object_or_404(Inventory, pk=pk)
        owner_id = inventory.owner_survivor.id
        survivor = get_object_or_404(Survivor, pk=owner_id)
        if survivor.infected:
            return Response(
                {"error": "Selected survivor is infected"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": 'Method "POST" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": 'Method "UPDATE" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": 'Method "DELETE" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class ReportViewSet(viewsets.ModelViewSet):

    queryset = Report.objects.all()
    serializer_class = ReportSerializer
