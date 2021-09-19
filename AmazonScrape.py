#!/usr/bin/env python3

import sys

from scrapy.crawler import CrawlerProcess # type: ignore
from scrapy.utils.project import get_project_settings # type: ignore

from scrapy_backend.scrapy_backend.spiders.amazon_spider import AmazonSpider # type: ignore

def get_categories():
    '''
    Returns a dictionary with numbers as keys, categories as values -> {1 : 'fashion',...}
    '''
    pass

if __name__ == '__main__':

    categories = get_categories()

    # default values

    # read input

    # create a CrawlerProcess
    process = CrawlerProcess(get_project_settings())

    # set AmazonSpider to crawl with given start_urls
    process.crawl(AmazonSpider, start_urls=[])

    # begin crawling
    process.start()
