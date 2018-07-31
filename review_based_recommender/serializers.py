from rest_framework import serializers
from .models import Spot, City


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('name', 'url')


class SpotSerializer(serializers.ModelSerializer):
    # city = CitySerializer()

    class Meta:
        model = Spot
        # fields = ('id', 'base_id', 'title', 'url', 'city')
        fields = ('id', 'title')
