import scrapy


class BaseItem(scrapy.Item):
    create_time = scrapy.Field()