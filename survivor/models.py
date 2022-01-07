from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import constraints
from survivor.choices import GENDER_CHOICES
# Create your models here.
class Survivor(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(120)])
    gender = models.CharField(max_length=25, choices=GENDER_CHOICES)
    latitude = models.FloatField(validators=[MinValueValidator(-90),MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180),MaxValueValidator(180)])
    infected = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    owner_survivor = models.OneToOneField(Survivor, on_delete=models.CASCADE, related_name='inventory')
    water = models.IntegerField(validators=[MinValueValidator(0)])
    food = models.IntegerField(validators=[MinValueValidator(0)])
    meds = models.IntegerField(validators=[MinValueValidator(0)])
    ammo = models.IntegerField(validators=[MinValueValidator(0)])
    def __str__(self):
        return self.owner_survivor.name + "'s inventory"


class Report(models.Model):
    gotReported = models.ForeignKey(Survivor, on_delete=models.CASCADE, related_name="reported")
    whoReported = models.ForeignKey(Survivor, on_delete=models.CASCADE, related_name="reports")
    
    class Meta:
        constraints = [models.UniqueConstraint(fields=['gotReported','whoReported'], name='unique_flag')]
    def __str__(self):
        return f"{self.gotReported} reported by {self.whoReported}"