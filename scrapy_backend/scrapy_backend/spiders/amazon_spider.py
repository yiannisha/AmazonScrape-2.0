#!/usr/bin/env python3

import re
import os

import scrapy  # type: ignore

from ..items import AmazonItem


class AmazonSpider(scrapy.Spider):
    """
    Spider for scraping Amazon list elements from Amazon's Movers&Shakers.
    """

    name = 'amazon'
    # start_urls set when creating, in AmazonScrape.py
    start_urls = [
        'https://www.amazon.com/gp/movers-and-shakers/electronics',
        #'https://www.amazon.com/HP-Chromebook-11-inch-Laptop-11a-na0010nr/dp/B08HJT1BKQ?_encoding=UTF8&psc=1'
    ]
    allowed_domains = ['amazon.com']

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
            sale_rank = self._clean_price(pattern, text)
        except TypeError:
            # Messages for debugging
            print('{} Sales Movement Text: {}'.format(self._get_no(elem), text))

        item['sales_rank'] = int(sale_rank)

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
                sales_perc = self._clean_price(pattern, text)
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

        return item

    def get_listing_prices(self, elem):
        '''
        Return a tuple of float prices if any have been found:
        None : if no price is found or offers exist
        (num, num) : if only a single price is found (num : <float>)
        (num1, num2) : if two or more prices are found (num1 : <float>, num2 : <float> | num1 < num2)

        :param elem: li element Selector object
        '''

        prices = []

        # check for offers
        offers = elem.css('span.a-color-secondary::text').get()
        if offers:
            self.log('{} has offers'.format(self._get_no(elem)))
            return None

        # search product's listing
        pattern = r'.?([\d\.]*)'
        prices.extend([
            self._clean_price(pattern, price.strip())
            # get all prices in product's listing
            for price in elem.css('span.p13n-sc-price::text').getall()
        ])
        # in case no prices are catalogued on product's listing
        if not prices:
            return None

        min_price, max_price = min(prices), max(prices)
        return min_price, max_price

    def get_product_page_prices(self, response):
        '''
        Return a tuple of float prices if any have been found:
        None, None: if no price is found
        (num, num) : if only a single price is found (num : <float>)
        (num1, num2) : if two or more prices are found (num1 : <float>, num2 : <float> | num1 < num2)

        :param response: Response object to be scraped
        '''

        prices = []

        # check availability
        avbl = (response.css('div#availability span::text').get().strip() == 'Currently unavailable')
        if avbl:
            self.log('Currently unavailable, returning None')
            # return None if not available
            return None, None

        # get prices from option A
        pattern = r'?([\d.,]*)'
        price = self._clean_price(pattern, response.css('span.a-offscreen::text').get().strip())
        if price:
            prices.append(price)

        # get prices from option B
        list_of_prices = [self._clean_price(pattern, price.strip())
                          for price in response.css('span.slot-price span::text').getall()
                          if price.strip()
                          ]

        # get all prices from page
        prices.extend(list_of_prices)

        # remove zeros
        prices = [price for price in prices if price > 0]

        return min(prices), max(prices)

    def _clean_price(self, pattern, price):
        '''
        Return a float from string of price.

        :param pattern: regex pattern to get first group of
        :param price: string of price to clean
        '''
        # debugging log messages
        # self.log('Clean Prices Input: {}'.format(price))
        price = float(re.search(pattern, price).groups()[0].replace(',', ''))
        # print('Clean Prices Output: {}'.format(price))
        return price

    def _request_product_page(self, item):
        '''
        Initiate a Request to the item["url"].

        !!!DOES NOT WORK FOR SOME REASON!!!
        (yield request must be in parse making this method obsolete)

        :param item: AmazonItem object
        '''
        self.log('Queuing Request for {}'.format(item['name']))
        request = scrapy.Request(url=item['url'],
                                 callback=self.parse_from_page,
                                 cb_kwargs=dict(item=item))
        self.log('URL: {}'.format(item['url']))
        self.log('Request: {}'.format(request))
        yield request

    def _get_no(self, elem):
        '''
        Returns list number of passed li Selector. To be used for debugging.

        :param elem: li element Selector
        '''

        list_num = elem.css('span.zg-badge-text::text').get()
        return list_num

    def parse_from_page(self, response, item):
        '''
        Search page for prices.
        Yield AmazonItem object with prices found. (None if not)

        :param response: Response object returned from scrapy's engine.
        :param item: AmazonItem with partially filled data
        '''

        self.log("Making request for {} page".format(item['name']))
        # get prices from product's page
        item['min_price'], item['max_price'] = self.get_product_page_prices(response)

        yield item

    def parse(self, response):
        '''
        Yield AmazonItem object if product's prices are found;
        Make new Request if product's prices not found.

        @url https://www.amazon.com/gp/movers-and-shakers/electronics
        @scrapes sales_rank sales_perc url name img_url min_price max_price

        :param response: Response object returned from scrapy's engine
        '''

        # assign response to a class variable to be used widely
        self.response = response

        # get all listed products
        li_elems = response.css('li.zg-item-immersion')

        for elem in li_elems:
            # get AmazonItem from collect_data with fields min_price, max_price empty
            elem_item = self.collect_data(elem)
            # get prices from product listing
            prices = self.get_listing_prices(elem)

            if prices:
                elem_item['min_price'], elem_item['max_price'] = prices
                yield elem_item
                continue
            else:
                # if no prices in product listing
                # Unfortunately, if the code below is put into another function
                # it doesn't work. Still haven't found out why.
                self.log('Queuing Request for {}'.format(elem_item['name']))
                request = scrapy.Request(url=elem_item['url'],
                                         callback=self.parse_from_page,
                                         cb_kwargs=dict(item=elem_item))
                yield request
                #self._request_product_page(elem_item)
                continue
