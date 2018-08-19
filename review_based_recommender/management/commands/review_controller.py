from django.core.management.base import BaseCommand
from ...models import Spot
import subprocess
import random
import os

class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.base_command = ['python', 'manage.py', 'get_review', '--spot-id']

    def handle(self, *args, **options):
        # スポット詳細ページからレビューを取得
        do_flag = True
        while do_flag:
            Spot.objects.filter()
