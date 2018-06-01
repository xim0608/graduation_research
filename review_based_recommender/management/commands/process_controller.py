from django.core.management.base import BaseCommand
from ...models import Spot, Review, SpreadsheetData
import subprocess

class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.spread_sheet = SpreadsheetData()
        self.base_command = ['python', 'manage.py', 'get_review', '--spot-id']

    def handle(self, *args, **options):
        do_flag = True
        while do_flag:
            subprocess.call(self.base_command + ['spot_id'])

