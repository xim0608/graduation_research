from django.core.management.base import BaseCommand
from ...models import Spot, SpreadsheetData, CityTask

class Command(BaseCommand):
    def __init__(self):
        self.spreadsheet = SpreadsheetData()

    def handle(self, *args, **options):
        print('lets set url')
        urls = self.spreadsheet.get_set_city_url()
        CityTask.import_urls(urls)
