# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    min_price = scrapy.Field()
    max_price = scrapy.Field()
    url = scrapy.Field()
    img_url = scrapy.Field()
    sales_perc = scrapy.Field()
    sales_rank = scrapy.Field()
