from django.contrib import admin
from survivor.models import Inventory, Report, Survivor
# Register your models here.

admin.site.register(Survivor)
admin.site.register(Report)
admin.site.register(Inventory)