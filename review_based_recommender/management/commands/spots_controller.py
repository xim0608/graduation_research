from django.core.management.base import BaseCommand
from ...models import City
import subprocess


class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.base_command = ['python', 'manage.py', 'get_spot', '--city-id']

    def handle(self, *args, **options):
        # 市内スポット一覧ページからスポットのurlを取得
        remained_cities = City.objects.filter(finish=False)
        if len(remained_cities) > 0:
            city = remained_cities[0]
            print(city.base_id)
            subprocess.call(self.base_command + [city.base_id])
