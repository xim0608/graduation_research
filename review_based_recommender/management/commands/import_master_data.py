from django.core.management.base import BaseCommand
from ...models import Prefecture, City, ZipCode
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
        elif options['type'] == 'postal':
            with codecs.open(os.getcwd() + '/review_based_recommender/KEN_ALL.CSV', "r", "Shift-JIS", "ignore") as file:
                df = pd.read_table(file, delimiter=",", header=None)
                for row in df.iterrows():
                    city_id = row[1][0]
                    zipcode = row[1][2]
                    z = ZipCode(city_id=city_id,zip_code=zipcode)
                    z.save()