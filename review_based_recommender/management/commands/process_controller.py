from django.core.management.base import BaseCommand
from ...models import Spot, Review, SpreadsheetData
import subprocess
import random
import time
from slackclient import SlackClient

class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.spread_sheet = SpreadsheetData()
        self.base_command = ['python', 'manage.py', 'get_review', '--spot-id']

    def handle(self, *args, **options):
        self.spread_sheet.set_spot_id()
        do_flag = True
        while do_flag:
            remained_tasks = self.spread_sheet.get_remained_spots_id()
            subprocess.call(self.base_command + [random.choice(remained_tasks)])
            do_flag = self.spread_sheet.task_remained()
