from graduation_research.lib import test_scripts
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--script', dest='script', required=True,
            help='script name in graduation_research/lib/test_scripts.py',
        )

    def handle(self, *args, **options):
        getattr(test_scripts, options['script'])()
