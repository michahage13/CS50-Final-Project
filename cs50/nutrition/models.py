from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import date

# Create your models here.
class macros(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    protein = models.IntegerField()
    fat = models.IntegerField()
    carbohydrates = models.IntegerField()
    date = models.DateField(default=date.today)
    cheat = models.BooleanField(default=False)
    comment = models.CharField(max_length=64, blank=True)
    description = models.CharField(max_length=2048, blank=True)
    image = models.ImageField(upload_to='images/', blank=True)

    def __str__(self):
        return (f"{self.id}, {self.protein}, {self.fat}, {self.carbohydrates}, {self.date}, {self.cheat}, {self.username}")
