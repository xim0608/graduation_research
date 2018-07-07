import os
from django.core.management.base import BaseCommand
from graduation_research.lib.graduation_research import GraduationResearch
import yaml

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
        elif method_name == 'all':
            setting_dir = os.getcwd() + '/graduation_research/lib'
            print(setting_dir)
            f = open("{}/settings.yml".format(setting_dir), "r+")
            data = yaml.load(f)
            for k in data:
                print('start: ' + k)
                GraduationResearch(method_name=k).save()
        else:
            GraduationResearch(method_name=method_name).save()
