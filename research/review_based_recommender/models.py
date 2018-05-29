from django.db import models


class Spot(models.Model):
    base_id = models.CharField(max_length=200)
    title = models.CharField(max_length=200)


class Review(models.Model):
    uid = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField()
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)


