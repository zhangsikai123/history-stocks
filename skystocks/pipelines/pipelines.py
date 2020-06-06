# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import ujson
from scrapy.middleware import logger
from skystocks.infra.cache.cache import caches
from skystocks.infra.persistence.database import Session, sessions
from skystocks.pipelines.models.stock import Stock
from datetime import datetime

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
        self.CODE_SET = 'stocks_code:date'
        self.insert_buffer = []
        self.buffer_threshold = 8000
        self.redis = caches['stocks-redis']
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
        if not self.insert_buffer:
            return
        begin_t = datetime.now()
        self.__do_persist(self.insert_buffer)
        end_t = datetime.now()
        time_elapsed = (end_t - begin_t).seconds
        logger.info('pipeline:batch persisence done::time for persist [{}s]\n'.format(time_elapsed))
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
        begin_t = datetime.now()
        logger.info('before dedup: data_list size: {}"'.format(len(wrapped_data_list)))
        wrapped_data_list = self.dedup(wrapped_data_list) # 去重
        logger.info('after dedup: data_list size: {}"'.format(len(wrapped_data_list)))
        end_t = datetime.now()
        time_elapsed = (end_t - begin_t).seconds
        logger.info('pipeline:deduplicate::time [{} s]'.format(time_elapsed))
        if len(wrapped_data_list) == 0:
            return
        try:
            self.session.add_all(wrapped_data_list)
            self.session.commit()
            self.redis.sadd(self.CODE_SET, *["{}:{}".format(d.code, d.date) for d in wrapped_data_list]) # 用于去重
        except Exception as e:
            # 目前采取一粒老鼠屎的策略，一批中有一个问题数据全部回滚，这样的问题是不够精细。小量的错误数据影响大量的本该被写入的数据的及时写入
            # 改进办法: 在表中加入hashcode字段表示联合索引的key，每次批量写入前先去除掉重复的再写入，或者将批量写入改为一个一个写入,或者使用redis set
            # 暂时不影响爬虫的使用，手动启动时可能需要特别注意开始时间的选择
            # 感觉应该专门写一个dedup func来解决这个问题
            self.session.rollback()
            logger.error("persist pipeline session failed due to {}, rollback...".format(e))
            return
        logger.info("{} data points persisted successfully".format(len(wrapped_data_list)))
    def data_hash_code(self, wrapped_data):
        return "{}:{}".format(wrapped_data.code, wrapped_data.date)

    def __check_dup(self, list_data, start, end):
        """
        返回{idx: is_dup::bool}
        inclusive
        """
        assert start >= 0 and end < len(list_data) and start < end
        ret = {}
        pipe = self.redis.pipeline()
        for i in range(start, end + 1):
            v = self.data_hash_code(list_data[i])
            pipe.sismember(self.CODE_SET, v)
        redis_out = pipe.execute()
        for i in range(start, end + 1):
            ret[i] = redis_out[i - start]
        return ret

    def dedup(self, list_data):
        batch_size = 1000
        i = 0
        l = len(list_data)
        ret = []
        while i < l:
            dups = self.__check_dup(list_data, i, min(i + batch_size - 1, l - 1))
            for idx, is_dup in dups.items():
                if is_dup:
                    continue
                ret.append(list_data[idx])
            i += batch_size
        return ret
