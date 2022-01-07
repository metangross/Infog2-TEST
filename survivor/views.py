from rest_framework.generics import get_object_or_404
from .models import Survivor, Inventory, Report
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .serializers import LocationSerializer, SurvivorSerializer, InventorySerializer, ReportSerializer
from rest_framework import status

from survivor import serializers

# Create your views here.


class SurvivorViewSet(viewsets.ModelViewSet):

    queryset = Survivor.objects.all()
    serializer_class = SurvivorSerializer
    
    def partial_update(self, request, *args, **kwargs):
        pk = kwargs['pk']
        survivor = get_object_or_404(Survivor, pk=pk)
        if(not survivor.infected):
            serializer = LocationSerializer(survivor, data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_serializer = SurvivorSerializer(survivor)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Selected survivor is infected"}, status=status.HTTP_400_BAD_REQUEST)
    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Method \"DELETE\" not allowed."},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
class InventoryViewSet(viewsets.ModelViewSet):
    
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer

class ReportViewSet(viewsets.ModelViewSet):
    
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    
