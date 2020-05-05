from datetime import datetime, timedelta
from random import shuffle
import scrapy
import ujson
from scrapy.exceptions import DropItem
from config.env import STAGE
from skystocks.items.history_item import HistoryStocksItem
from skystocks.spiders.seeds_collect import CodeCollect


class QueryGen(object):
    host = 'q.stock.sohu.com'

    @classmethod
    def __to_url(cls, host, query_body):
        if 'http://' not in host:
            host = 'http://' + host + '/hisHq?'
        body = '/'
        for k, v in query_body.items():
            the_and = '' if body[-1] == '?' else '&'
            body += the_and + (str(k) + '=' + str(v))
        return host + body

    @classmethod
    def stock_data_query(cls, start, end, code):
        """search stock data by start and end date"""
        if start > end:
            raise Exception("start {} should be smaller than end {}".format(
                start, end
            ))
        query_body = dict(
            code=str(code),
            start=start,
            end=end,
            stat='1',
            order='D',
            period='d',
            callback='historySearchHandler',
            rt='jsonp'
        )

        query_url = cls.__to_url(cls.host, query_body)
        return query_url


class HistoryStockSpider(scrapy.Spider):
    DATE_FORMAT = "%Y%m%d"
    name = 'history_stocks'
    start_date = '19990101'
    interval = 500
    end_date = datetime.now().strftime(DATE_FORMAT)
    stock_dir = CodeCollect().data()  # index for stock market {code:{'name': '***'}
    response_data_format = ['date', 'open', 'close', 'rise', 'rise_rate', 'lowest', 'highest', 'trading_volume',
                            'turnover', 'turnover_rate']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        code_pool = list(set(self.stock_dir.keys()))
        shuffle(code_pool)
        if STAGE in ['dev', 'test']:
            self.logger.info('stage is dev')
            code_pool = code_pool[:1]
        else:
            self.logger.info('stage is prod')
        self.code_pool = code_pool

    def start_requests(self):
        for code in self.code_pool:
            start_date = getattr(self, 'start_date', self.start_date)
            end_date = (datetime.strptime(start_date, self.DATE_FORMAT) + timedelta(days=self.interval)).strftime(self.DATE_FORMAT)
            url = QueryGen.stock_data_query(start_date, end_date, code)
            yield scrapy.Request(url=url, callback=self.parse,
                                 cb_kwargs={'start_date': start_date, 'end_date': end_date, 'code': code})

    def parse(self, response, **cb_kwargs):
        code = cb_kwargs['code']
        yield self.__process_hq(response, code)

        # date add could be complicated
        start_date = (datetime.strptime(cb_kwargs['end_date'], self.DATE_FORMAT) + timedelta(days=1)).strftime(
            self.DATE_FORMAT)
        end_date = (datetime.strptime(cb_kwargs['end_date'], self.DATE_FORMAT) + timedelta(
            days=self.interval)).strftime(self.DATE_FORMAT)
        cb_kwargs['start_date'] = start_date
        cb_kwargs['end_date'] = end_date

        # 终止条件, response 最小日期大于设定终止日期
        if start_date < self.end_date:
            next_query = QueryGen.stock_data_query(start_date, end_date, code)
            yield response.follow(next_query, callback=self.parse, cb_kwargs=cb_kwargs)

    def __process_hq(self, response, code):
        body = response.text
        body = ujson.loads(body[21:-2])
        if len(body) == 0 or 'hq' not in body[0]:
            self.logger.error("empty response for {}".format(response.url))
            return

        hq = body[0]['hq']
        cn_name = self.stock_dir[code]['name']
        history = HistoryStocksItem()
        stock_items = []
        for item in hq:
            stock_item = {'code': code, 'cn_name': cn_name}
            for i, k in enumerate(self.response_data_format):
                try:
                    stock_item[k] = item[i]
                except Exception:
                    raise DropItem("k, v mismatch {}/{}".format(
                        str(self.response_data_format), str(item)
                    ))
            stock_items.append(stock_item)
        history['stock_items'] = stock_items
        return history

    @property
    def sample(self):
        query = QueryGen.stock_data_query(self.start_date, self.start_date, self.code_pool[0])
        return scrapy.Request(url=query, callback=self.parse)
