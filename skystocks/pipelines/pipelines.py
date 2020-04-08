# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import ujson
from scrapy.middleware import logger

from skystocks.infra.persistence.database import Session, sessions
from skystocks.pipelines.models.stock import Stock


class JsonPipeline(object):

    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = ujson.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class PersistPipeline(object):

    def __init__(self):
        self.session = None

        self.insert_buffer = []
        self.buffer_threshold = 8000

    def open_spider(self, spider):
        session_cls = sessions['stocks']
        self.session = session_cls()

    def close_spider(self, spider):
        self.__flush_buffer()
        self.session.close()

    def process_item(self, history, spider):
        if not history or not history['stock_items']:
            # fail fast
            logger.error("pipeline error: empty hitory")
            return
        self.insert_buffer.extend(history['stock_items'])
        if len(self.insert_buffer) >= self.buffer_threshold:
            self.__flush_buffer()
        return history

    def __flush_buffer(self):
        self.__do_persist(self.insert_buffer)
        self.insert_buffer = []

    def __do_persist(self, stock_items):
        wrapped_data_list = []
        for stock_item in stock_items:
            # make 2020-03-01 ==> int(20200301)
            stock_item['date'] = int(stock_item['date'].replace('-', ''))
            stock_item['rise_rate'] = stock_item['rise_rate'].replace("%", "")
            if stock_item['turnover_rate'] == '-':
                stock_item['turnover_rate'] = -1
            else:
                stock_item['turnover_rate'] = stock_item['turnover_rate'].replace("%", "")

            wrapped = Stock(**stock_item)
            wrapped_data_list.append(wrapped)
        try:
            self.session.add_all(wrapped_data_list)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error("persist pipeline session failed due to {}, rollback...".format(e))
