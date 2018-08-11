from django.core.management.base import BaseCommand
from locations.models import Prefecture, City
import pandas as pd
import os
import codecs


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--type', dest='type', required=True,
            help='specify master type',
        )

    def handle(self, *args, **options):
        if options['type'] == 'pref':
            df = pd.read_csv(os.getcwd() + '/review_based_recommender/h2905puboffice_utf8.csv')
            pref_id = 1
            for row in df.iterrows():
                if int(row[1].jiscode) % 1000 == 0:
                    Prefecture.objects.create(id=pref_id, name=row[1]['name'], name_kana=row[1].namekana,
                                              lat=row[1].lat, lon=row[1].lon)
                    pref_id += 1
        elif options['type'] == 'city':
            df = pd.read_csv(os.getcwd() + '/review_based_recommender/h2905puboffice_utf8.csv')
            pref_id = 1
            prefecture = None
            for row in df.iterrows():
                if int(row[1].jiscode) % 1000 == 0:
                    prefecture = Prefecture.objects.get(id=pref_id)
                    pref_id += 1
                else:
                    City.objects.create(id=row[1]['jiscode'], name=row[1]['name'], name_kana=row[1].namekana,
                                        lat=row[1].lat, lon=row[1].lon, prefecture=prefecture)
