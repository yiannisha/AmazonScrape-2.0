#!/usr/bin/env python3

import sys

from scrapy.crawler import CrawlerProcess # type: ignore
from scrapy.utils.project import get_project_settings # type: ignore

from scrapy_backend.scrapy_backend.spiders.amazon_spider import AmazonSpider # type: ignore

from scrapy_backend.categories import categories # type: ignore

if __name__ == '__main__':

    # default values

    # read input

    # create a CrawlerProcess
    process = CrawlerProcess(get_project_settings())

    # set AmazonSpider to crawl with given start_urls
    process.crawl(AmazonSpider, start_urls=[])

    # begin crawling
    process.start()
