from django.core.management.base import BaseCommand
from ...models import Spot
from review_based_recommender.lib.crawlers import SpotPage
from django.db.models import F
import os
import slackweb
import time
from socket import gethostname

ta_spot_slack = slackweb.Slack(url=os.environ.get('SLACK_WEBHOOK_URL_2'))


class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.base_command = ['python', 'manage.py', 'get_review', '--spot-id']

    def add_arguments(self, parser):
        parser.add_argument(
            '--mod', dest='mod', required=True,
            help='modulo by two',
        )

    def handle(self, *args, **options):
        # スポット詳細ページからレビューを取得
        # 市内スポット一覧ページからスポットのurlを取得
        # mod: 0/2, 1/2 or 0/3, 1/3, 2/3...etc
        if '/' in options['mod']:
            remain, mod = options['mod'].split('/')
            remain = int(remain)
            mod = int(mod)
            remained_spots = Spot.objects.annotate(idmod2=F('id') % mod).filter(is_updatable=True, idmod2=remain)
            for remained_spot in remained_spots:
                try:
                    SpotPage(remained_spot.base_id).get()
                    print('finish spots')
                except Exception as e:
                    print('errored')
                    print("type: {}".format(type(e)))
                    print("msg: {}".format(str(e)))
                    ta_spot_slack.notify(
                        text="error in crawl spot: {}, url: {}, host: {}".format(remained_spot.base_id,
                                                                                 remained_spot.url,
                                                                                 gethostname()))
                time.sleep(2)

        else:
            remained_spots = Spot.objects.filter(is_updatable=True)
            for remained_spot in remained_spots:
                try:
                    SpotPage(remained_spot.base_id).get()
                except Exception as e:
                    print('errored')
                    print("type: {}".format(type(e)))
                    print("msg: {}".format(str(e)))
                    ta_spot_slack.notify(text="error in crawl spot: {}, url: {}, host: {}".format(remained_spot.base_id,
                                                                                                  remained_spot.url,
                                                                                                  gethostname()))
                time.sleep(2)
