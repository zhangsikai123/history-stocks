# -*- coding: utf-8 -*-

# Define here the models for your scraped items
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy import Field
from scrapy.loader import ItemLoader, Identity
from skystocks.items.base_item import BaseItem


class StockItem(BaseItem):
    code = Field()
    cn_name = Field()
    date = Field(serializer=str)  # 日期
    open = Field()  # 开盘价
    close = Field()  # 收盘价
    rise = Field()  # 涨跌额
    rise_rate = Field()  # 涨跌率: %
    lowest = Field()  # 最低
    highest = Field()  # 最高
    trading_volume = Field()  # 成交量
    turnover = Field()  # 成交额: 万
    turnover_rate = Field()  # 换手率: %

    def __repr__(self):
        """only print out attr1 after exiting the Pipeline"""
        return "{}|{}|{}".format(self.cn_name, self.code, self.date)


class HistoryStocksItem(BaseItem):
    stock_items = Field()

    def __repr__(self):
        return "" # no log out


class StockItemLoader(ItemLoader):
    default_input_processor = Identity()
