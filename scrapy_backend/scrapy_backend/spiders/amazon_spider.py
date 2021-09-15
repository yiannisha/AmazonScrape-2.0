#!/usr/bin/env python3

import re
import os

import scrapy

from ..items import AmazonItem


class AmazonSpider(scrapy.Spider):
    """
    Spider for scraping Amazon list elements from Amazon's Movers&Shakers.
    """

    name = 'amazon'
    # start_urls set when creating, in AmazonScrape.py
    start_urls = [
        'https://www.amazon.com/gp/movers-and-shakers/electronics',
    ]

    def __init__(self):
        """scrapy.Spider __init__."""
        # Add start_urls if check run detected
        if os.environ.get('SCRAPY_CHECK'):
            self.start_urls = [
            'https://www.amazon.com/gp/movers-and-shakers/books/',
            'https://www.amazon.com/gp/movers-and-shakers/electronics',
            ]

    def collect_data(self, elem):
        '''
        Return an AmazonItem object with all the fields required.

        :param elem: li element Selector of item in an ordered list
        '''

        item = AmazonItem()

        # sales rank
        pattern = r'Sales rank: ([\d,]*)'
        text = elem.css('span.zg-sales-movement::text').get()
        try:
            sale_rank = re.search(pattern, text).groups()[0]
        except TypeError:
            # Messages for debugging
            print('{} Sales Movement Text: {}'.format(self._get_no(elem), text))

        sale_rank = int(sale_rank.replace(',', ''))
        item['sales_rank'] = sale_rank

        # sales percentage
        # Previously unranked products do not have a sales percentage

        # Check if previously unranked
        pattern = 'previously unranked'
        text = elem.css('span.zg-sales-movement::text').get()
        if not bool(re.search(pattern, text)):
            # proceed normally if not previously unranked
            pattern = r'([\d,]*)'
            text = elem.css('span.zg-percent-change::text').get()
            try:
                sales_perc = re.search(pattern, text).groups()[0]
            except TypeError:
                # Message for debugging
                print('{} Sales Percentage Text: {}'.format(self._get_no(elem), text))

                sales_perc = int(sales_perc.replace(',', ''))
        else:
            sales_perc = None

        item['sales_perc'] = sales_perc

        # product url
        semi_url = elem.css('a.a-link-normal::attr(href)').get()
        item['url'] = self.response.urljoin(semi_url)

        # product name
        item['name'] = elem.css('a.a-link-normal div::text').get().strip()

        # image url
        item['img_url'] = elem.css('a.a-link-normal div img::attr(src)').get()

        # TEMPORARY
        # min_price and max_price
        # price = elem.css('span.p13n-sc-price::text').get()
        item['min_price'], item['max_price'] = self.get_prices(elem, item['url'])

        return item

    def get_prices(self, elem, url):
        '''
        Returns a tuple based on prices found:
        (None, None) : if no price is found
        (num, num) : if only a single price is found (num : <float>)
        (num1, num2) : if two or more prices are found (num1 : <float>, num2 : <float> | num1 < num2)

        :param elem: li element Selector object
        :param url: product's url -> <string>
        '''

        # search product's listing

        # search product's page
        # TODO : create Request to product's page
        # TODO: create secondary method to be used as a callback function
        raise NotImplementedError

        return min_price, max_price

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

        @url https://www.amazon.com/gp/movers-and-shakers/electronics
        @scrapes sales_rank sales_perc url name img_url min_price max_price
        '''

        # assign response to a class variable to be used widely
        self.response = response

        # get all listed products
        li_elems = response.css('li.zg-item-immersion')

        for elem in li_elems:
            yield self.collect_data(elem)
