from django.core.management.base import BaseCommand
from ...models import Spot, Review, SpreadsheetData, City
import subprocess
import random
import os

class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.spreadsheet = SpreadsheetData()
        self.base_command = ['python', 'manage.py', 'get_spot', '--city-id']

    def handle(self, *args, **options):
        urls = self.spreadsheet.get_set_city_url()
        City.import_urls(urls)
        remained_cities = City.objects.filter(finish=False)
        if len(remained_cities) > 0:
            city = remained_cities[0]
            print(city.base_id)
            subprocess.call(self.base_command + [city.base_id])
