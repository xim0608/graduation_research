from django.db import models
from oauth2client.service_account import ServiceAccountCredentials
from locations.models import City
import gspread
import os
import sys
from django.db.models.signals import post_save
from django.dispatch import receiver


class Spot(models.Model):
    base_id = models.CharField(max_length=200, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    url = models.CharField(max_length=200, unique=True)
    count = models.IntegerField(default=0, null=True, blank=True)
    total_count = models.IntegerField(default=None, null=True, blank=True)
    all_lang_total_count = models.IntegerField(default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_updatable = models.BooleanField(default=False)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        if self.count != 0:
            return 'spot={}, count={}/{}'.format(self.title, self.count, self.total_count)
        else:
            return 'url={}'.format(self.url)

    def update_count(self, count):
        self.count = self.count + count
        self.save()

    @classmethod
    def remained_tasks(cls):
        remained_tasks = Spot.objects.filter(total_count=None)
        doing_or_done_tasks = Spot.objects.exclude(total_count=None)
        remained_tasks_list = list(remained_tasks)
        doing_or_done_tasks_list = list(doing_or_done_tasks)
        if len(doing_or_done_tasks) > 0:
            for task in doing_or_done_tasks_list:
                if task.total_count - task.count > 0:
                    remained_tasks_list.append(task)
        return remained_tasks_list

    @classmethod
    def import_urls(cls, urls):
        for url in urls:
            Spot.objects.get_or_create(url=url)

    def reviews(self):
        return Review.objects.filter(spot_id=self.id)


@receiver(post_save, sender=Spot)
def create_spot(sender, instance, created, **kwargs):
    if created:
        # set spot base id
        tmp = instance.url.split('Attraction_Review-')[1].split('-Reviews')[0]
        instance.base_id = tmp
        if Spot.objects.filter(base_id=tmp).exists():
            instance.delete()
        else:
            instance.save()


class SpotImage(models.Model):
    class Meta:
        db_table = 'spot_images'
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    license = models.IntegerField()
    height = models.IntegerField()
    width = models.IntegerField()
    owner = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)


class Review(models.Model):
    username = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField()
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)

    def __str__(self):
        return 'spot={}, title={}'.format(self.spot.title, self.title)


class SpreadsheetData():
    data_column = ['url', 'spot_id', 'spot_name', 'reviews', 'count', ' remain', 'finish']

    def __init__(self):
        scopes = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
        directory = os.path.dirname(os.path.abspath(__file__))
        json_file = "/client_secret.json"
        credentials = ServiceAccountCredentials.from_json_keyfile_name(directory + json_file, scopes=scopes)
        # http_auth = credentials.authorize(Http())
        self.gc = gspread.authorize(credentials)
        self.wb = self.gc.open("クローラー管理")
        self.sh = self.wb.sheet1

    def get_set_url(self):
        return self.sh.col_values(1)[1:]

    def get_set_city_url(self):
        return self.wb.worksheet("シート2").col_values(1)[1:]

    def get_remained_spots_id(self):
        flags = self.sh.col_values(6)
        spot_ids = self.sh.col_values(2)
        reviews_num = self.sh.col_values(4)
        del (spot_ids[0])
        del (flags[0])
        tasks = []
        for idx, spot_id in enumerate(spot_ids):
            try:
                if int(flags[idx]) > 0 and reviews_num[idx] is not '':
                    tasks.append(spot_id)
            except:
                print("Unexpected error:", sys.exc_info()[0])
        return tasks

    def task_remained(self):
        tasks = self.get_remained_spots_id()
        if len(tasks) > 0:
            return True
        else:
            return False

    def set_spot_id(self):
        url_list = self.sh.col_values(1)
        del (url_list[0])
        print(url_list)
        spot_ids = []
        for url in url_list:
            try:
                tmp = url.split('Attraction_Review-')[1].split('-Reviews')[0]
                print(tmp)
                spot_ids.append(tmp)
            except:
                print("url error: {}".format(url))
                print("Unexpected error:", sys.exc_info()[0])
                spot_ids.append('')
        cell_list = self.sh.range("B2:B{}".format(len(url_list) + 1))
        for index, cell in enumerate(cell_list):
            cell.value = spot_ids[index]
        self.sh.update_cells(cell_list)

    def find_by_spot_id(self, spot_id):
        cell_list = self.sh.findall(spot_id)
        if len(cell_list) == 0:
            row = cell_list[0].row
        else:
            # TODO: indexが1以上のものを削除する
            row = cell_list[0].row
        row_values = self.sh.row_values(row)
        print(row_values)
        return self.convert_row(row_values)

    def update_count_cell_by_spot_id(self, spot_id, count):
        cell = self.sh.find(spot_id)
        row = cell.row
        count_before = self.sh.acell("E{}".format(row)).value
        if count_before == '':
            count_before = 0
        self.sh.update_acell("E{}".format(row), int(count_before) + count)

    def record_first_page_info(self, spot_id, first_page_info):
        title = first_page_info[1]
        review_num = first_page_info[0]
        cell = self.sh.find(spot_id)
        row = cell.row
        self.sh.update_acell("C{}".format(row), title)
        self.sh.update_acell("D{}".format(row), review_num)

    @classmethod
    def convert_row(cls, row_values):
        h = {}
        for index, row_value in enumerate(row_values):
            h[cls.data_column[index]] = row_value
        return h
