from django.core.management.base import BaseCommand
from review_based_recommender.lib.crawlers import PrefPage


class Command(BaseCommand):
    help = 'Get Cities From Cities List (Prefecture Top)'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
    delay = 10

    def add_arguments(self, parser):
        parser.add_argument(
            '--pref-id', dest='pref-id', required=True,
            help='pref-id to get review',
        )

    def handle(self, *args, **options):
        # saitama: g298175
        # 初期化データがあるので、このスクリプトを動かす必要はない
        pref_id = options['pref-id']
        PrefPage(pref_id).get()
