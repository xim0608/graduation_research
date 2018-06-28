from django.core.management.base import BaseCommand
from graduation_research.lib.graduation_research import GraduationResearch


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--method', dest='method_name', required=False,
            help='method_name in settings.yml',
        )

    def handle(self, *args, **options):
        method_name = options['method_name']
        if method_name is None:
            GraduationResearch().save()
        else:
            GraduationResearch(method_name=method_name).save()
