from django.core.management.base import BaseCommand
from ...models import Spot, Review

class Command(BaseCommand):
    help = 'Get Review From Page'

    # def add_arguments(self, parser):

    def hello(self):
        print('hello')

    def handle(self, *args, **options):
        self.hello()
