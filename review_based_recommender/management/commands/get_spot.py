from django.core.management.base import BaseCommand
from review_based_recommender.lib.crawlers import CityPage


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--city-id', dest='city-id', required=True,
            help='city-id to get spots',
        )

    def handle(self, *args, **options):
        city_id = options['city-id']
        CityPage(city_id).get()
