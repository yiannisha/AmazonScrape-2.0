#!/usr/bin/env python3

import re, os
import scrapy
from ..items import AmazonItem

class AmazonSpider(scrapy.Spider):
    '''
    Spider for scraping Amazon list elements from Amazon's Movers&Shakers
    '''

    name = 'amazon'
    # start_urls set when creating, in AmazonScrape.py

    def __init__(self):
        # Add start_urls if check run detected
        if os.environ.get('SCRAPY_CHECK'):
            self.start_urls = [
            'https://www.amazon.com/gp/movers-and-shakers/books/',
            ]

    def collect_data(self, elem):
        '''
        Returns an AmazonItem object with all the fields required.

        :param elem: li element Selector of item in an ordered list
        '''

        item = AmazonItem()

        # sales rank
        pattern = 'Sales rank: ([\d,]*)'
        text = elem.css('span.zg-sales-movement::text').get()
        try:
            sale_rank = re.search(pattern, text).groups()[0]
        except TypeError:
            print('{} Sales Movement Text: {}'.format(self._get_no(elem), text))
        sale_rank = int(sale_rank.replace(',',''))
        item['sales_rank'] = sale_rank

        # sales percentage
        pattern = '([\d,]*)'
        text = elem.css('span.zg-percent-change::text').get()
        try:
            sales_perc = re.search(pattern, text).groups()[0]
        except TypeError:
            print('{} Sales Percentage Text: {}'.format(self._get_no(elem), text))
        sales_perc = int(sales_perc.replace(',',''))
        item['sales_perc'] = sales_perc

        # product url
        semi_url = elem.css('a.a-link-normal::attr(href)').get()
        item['url'] = self.response.urljoin(semi_url)

        # product name
        item['name'] = elem.css('a.a-link-normal div::text').get().strip()

        # image url
        item['img_url'] = elem.css('a.a-link-normal div img::attr(src)').get()

        return item

    def _get_no(self, elem):
        '''
        Returns list number of passed li Selector. To be used for debugging.

        :param elem: li element Selector
        '''

        list_num = elem.css('span.zg-badge-text::text').get()
        return list_num

    def parse(self, response):
        '''
        Data is scraped.
        Further requests are made.

        @url https://www.amazon.com/gp/movers-and-shakers/books/
        @scrapes sales_rank sales_perc url name img_url
        '''

        # assign response to a class variable to be used widely
        self.response = response

        # get all listed products
        li_elems = response.css('li.zg-item-immersion')

        for elem in li_elems:
            yield self.collect_data(elem)
