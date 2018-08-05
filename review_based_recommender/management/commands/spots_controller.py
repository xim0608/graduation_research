from django.core.management.base import BaseCommand
from ...models import Spot, Review, SpreadsheetData, CityTask
import subprocess
import random
import os


class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.spreadsheet = SpreadsheetData()
        self.base_command = ['python', 'manage.py', 'get_spot', '--city-id']

    def handle(self, *args, **options):
        # 市内スポット一覧ページからスポットのurlを取得
        urls = self.spreadsheet.get_set_city_url()
        CityTask.import_urls(urls)
        remained_cities = CityTask.objects.filter(finish=False)
        if len(remained_cities) > 0:
            city = remained_cities[0]
            print(city.base_id)
            subprocess.call(self.base_command + [city.base_id])
