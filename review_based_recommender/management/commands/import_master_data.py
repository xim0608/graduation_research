from django.core.management.base import BaseCommand
from ...models import Prefecture
import pandas as pd
import os


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--type', dest='type', required=True,
            help='specify master type',
        )

    def handle(self, *args, **options):
        df = pd.read_csv(os.getcwd() + '/review_based_recommender/h2905puboffice_utf8.csv')
        if options['type'] == 'pref':
            pref_id = 1
            for row in df.iterrows():
                if int(row[1].jiscode) % 1000 == 0:
                    Prefecture.objects.create(id=pref_id, name=row[1]['name'], name_kana=row[1].namekana,
                                              lat=row[1].lat, lon=row[1].lon)
                    pref_id += 1
        else:
            pass
