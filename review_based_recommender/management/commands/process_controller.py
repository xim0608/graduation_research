from django.core.management.base import BaseCommand
from ...models import Spot, Review, SpreadsheetData
import subprocess
import random
import os

class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.base_command = ['python', 'manage.py', 'get_review', '--spot-id']

    def handle(self, *args, **options):
        do_flag = True
        while do_flag:
            remained_tasks = Spot.remained_tasks()
            task = random.choice(remained_tasks)
            subprocess.call(self.base_command + [task.base_id])

            # check remain tasks
            remained_tasks = Spot.remained_tasks()
            if len(remained_tasks) > 0:
                do_flag = True
            else:
                do_flag = False
            if os.environ.get('DEBUG') == 'TRUE':
                pass
            else:
                subprocess.call("ps aux | grep chrome | grep -v grep | awk '{ print \"kill -9\", $2 }' | sh")
