from django.contrib import admin

from .models import Spot, Review, CityTask

# Register your models here.
admin.site.register(Spot)
admin.site.register(Review)
admin.site.register(CityTask)
