from django.core.management.base import BaseCommand
from review_based_recommender.lib.crawlers import SpotPage


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--spot-id', dest='spot-id', required=True,
            help='spot-id to get review',
        )

    def handle(self, *args, **options):
        spot_id = options['spot-id']
        SpotPage(spot_id).get()

