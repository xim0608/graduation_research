from django.core.management.base import BaseCommand
from ...models import Review
import logging
from logging import getLogger, StreamHandler, Formatter, FileHandler
import slackweb
import os


class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.logger = getLogger("Review Progress")
        self.logger.setLevel(logging.DEBUG)
        stream_handler = StreamHandler()
        file_handler = FileHandler('crawl_progress.log', 'a')
        handler_format = Formatter('%(asctime)s - %(message)s')
        stream_handler.setFormatter(handler_format)
        file_handler.setFormatter(handler_format)
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        stream_handler.setLevel(logging.DEBUG)

    def handle(self, *args, **options):
        f = open('crawl_progress.log', 'r')
        last_line = f.readlines()[-1].strip()
        f.close()
        infos = last_line.split(' - ')
        now_count = Review.objects.all().count()
        print(infos)
        slack = slackweb.Slack(url=os.environ.get('SLACK_WEBHOOK_URL'))
        if infos:
            last_time = infos[0].split(',')[0]
            slack.notify(text="<!channel>\n前回取得時刻： {}、取得数: {}\n現在取得数： {}, 前回からの進捗： {}"
                         .format(last_time, infos[1], now_count, now_count-int(infos[1])))
        self.logger.info(now_count)

