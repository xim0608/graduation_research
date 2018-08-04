from rest_framework import serializers
from .models import Spot, CityTask, SpotImage


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CityTask
        fields = ('name', 'url')


class SpotImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotImage
        fields = ('url', 'license', 'height', 'width', 'owner', 'owner_name')


class SpotSerializer(serializers.ModelSerializer):
    # city = CitySerializer()
    image = serializers.SerializerMethodField()

    def get_image(self, instance):
        return SpotImageSerializer(instance.spotimage_set.first()).data

    class Meta:
        model = Spot
        # fields = ('id', 'base_id', 'title', 'url', 'city')
        fields = ('id', 'title', 'url', 'image')

