from django.core.management.base import BaseCommand
from locations.models import CityAppend
from django.db.models import F
from review_based_recommender.lib.crawlers import CityPage
import subprocess
import time
import os
import slackweb
from socket import gethostname


ta_slack = slackweb.Slack(url=os.environ.get('SLACK_WEBHOOK_URL'))


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
        if mod == 0 or mod == 1:
            do_flag = True
            while do_flag:
                remained_city = CityAppend.objects.annotate(idmod2=F('city_id') % 2).filter(idmod2=mod,
                                                                                            finish=False).first()
                try:
                    CityPage(remained_city.ta_area_id).get()
                except:
                    print('errored')
                    ta_slack.notify(text="error in crawl city: {}, id: {}, host: {}".format(remained_city.city.name, remained_city.city.ta_area_id, gethostname()))
                time.sleep(2)
                if CityAppend.objects.annotate(idmod2=F('city_id') % 2).filter(idmod2=mod, finish=False).count() == 0:
                    do_flag = False
                    print('no more cities')
        else:
            do_flag = True
            while do_flag:
                remained_city = CityAppend.objects.filter(finish=False).first()
                try:
                    CityPage(remained_city.ta_area_id).get()
                except:
                    print('errored')
                    ta_slack.notify(text="error in crawl city: {}, id: {}, host: {}".format(remained_city.city.name, remained_city.city.ta_area_id, gethostname()))
                time.sleep(2)
                if CityAppend.objects.filter(finish=False).count() == 0:
                    do_flag = False
                    print('no more cities')
