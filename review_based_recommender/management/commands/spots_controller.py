from django.core.management.base import BaseCommand
from ...models import CityAppend
import subprocess


class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.base_command = ['python', 'manage.py', 'get_spot', '--city-id']

    def handle(self, *args, **options):
        # 市内スポット一覧ページからスポットのurlを取得
        remained_cities = CityAppend.objects.filter(finish=False)
        if len(remained_cities) > 0:
            city = remained_cities[0]
            subprocess.call(self.base_command + [city.ta_area_id])
