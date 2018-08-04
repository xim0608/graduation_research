from django.core.management.base import BaseCommand
from ...models import Spot, City
import re


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--type', dest='type', required=True,
            help='specify migrate type',
        )

    def handle(self, *args, **options):
        if options['type'] == 'first':
            # titleに含まれる最後の()から抜き出す
            spots = Spot.objects.all()
            counter = 0
            for spot in spots:
                try:
                    cities = City.objects.filter(name=spot.title.split('(')[1].split(')')[0])
                    city = cities[0]
                    spot.city = city
                    spot.save()
                except:
                    counter += 1
            print(counter)
        elif options['type'] == 'second':
            cities = City.objects.filter(prefecture__id__in=[11,12,13,14,19,22])
            spots = Spot.objects.filter(city=None)
            for city in cities:
                for spot in spots:
                    if city.name in spot.title:
                        print("{}:{}".format(city.name, spot.title))
                        spot.city = city
                        spot.save()
                        continue
        elif options['type'] == 'city_task_to_city_appends':
            pass
