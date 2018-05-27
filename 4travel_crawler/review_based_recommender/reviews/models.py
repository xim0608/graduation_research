from django.db import models


class Prefecture(models.Model):
    name = models.CharField(max_length=140)
    path = models.CharField(max_length=140)
    # ex. http://4travel.jp/dm_area_todofuken-kanagawa.html


class Area(models.Model):
    prefecture = models.ForeignKey(Prefecture)
    name = models.CharField(max_length=140)
    path = models.CharField(max_length=140)
    # ex. http://4travel.jp/dm_area_kuchoson-enoshima.html
    list_path = models.CharField(max_length=140)


class AreaListPage(models.Model):
    area = models.ForeignKey(Area)


# class Spot(models.Model):