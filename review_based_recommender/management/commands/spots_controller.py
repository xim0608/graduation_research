from django.core.management.base import BaseCommand
from locations.models import CityAppend
from django.db.models import F
import subprocess
import time


class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.base_command = ['python', 'manage.py', 'get_spot', '--city-id']

    def add_arguments(self, parser):
        parser.add_argument(
            '--mod', dest='mod', required=True,
            help='modulo by two',
        )

    def handle(self, *args, **options):
        # 市内スポット一覧ページからスポットのurlを取得
        # mod: 0 or 1
        mod = int(options['mod'])
        do_flag = True
        while do_flag:
            remained_city = CityAppend.objects.annotate(idmod2=F('city_id') % 2).filter(idmod2=mod, finish=False).first()
            subprocess.call(self.base_command + [remained_city.ta_area_id])
            time.sleep(2)
            if CityAppend.objects.annotate(idmod2=F('city_id') % 2).filter(idmod2=mod, finish=False).count() == 0:
                do_flag = False
                print('no more cities')
