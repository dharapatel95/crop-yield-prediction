from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crop = models.CharField(max_length=100)
    season = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    area = models.FloatField()
    #production = models.FloatField()
    fertilizer = models.FloatField()
    pesticide = models.FloatField()

    avg_temp_c = models.FloatField()
    total_rainfall_mm = models.FloatField()
    avg_humidity_percent = models.FloatField()

    #n = models.FloatField()
    #p = models.FloatField()
    #k = models.FloatField()
    #ph = models.FloatField()

    result = models.FloatField()

    def __str__(self):
        return self.crop
