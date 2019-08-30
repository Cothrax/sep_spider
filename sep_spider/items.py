# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose


class SepItemLoader(scrapy.loader.ItemLoader):
    default_output_processor = TakeFirst()


class SepItem(scrapy.Item):
    url = scrapy.Field()
    file_url = scrapy.Field(
        output_processor=MapCompose(lambda x: x)
    )
    name = scrapy.Field()
    file_path = scrapy.Field()
