#!/usr/bin/env python3

import sys
import os
import argparse

from scrapy.crawler import CrawlerProcess # type: ignore
from scrapy.utils.project import get_project_settings # type: ignore

from scrapy_backend.scrapy_backend.spiders.amazon_spider import AmazonSpider # type: ignore

from scrapy_backend.categories import categories # type: ignore

def parse_from_cli():
    '''
    Parse arguments passed from command line.

    :param category: number corresponding to category, based on categories_list.txt
    :param format: format of file to be saved as
    :param limit: number of max results AmazonSpider returns
    :param file: path to file that data will be saved as
    :param append: True to append to file passed, False to write new file
    '''

    USAGE = './AmazonScrape.py -c 18 -f json -l 57 -p ~/demo.json -a'

    parser = argparse.ArgumentParser(
            usage=USAGE,
            description='Scrape data from Amazon Movers&Shakers')

    # add arguments to parser
    # category
    parser.add_argument('-c', action='store', type=int, required=True,
                        help='Number corresponding to category, based on categories_list.txt.')
    # format
    parser.add_argument('-f', action='store', type=str, default='csv',
                        help='Format of file to be saved as.')
    # limit
    parser.add_argument('-l', action='store', type=int, default=100,
                        help='Νumber of max scraped products to return.')
    # file
    parser.add_argument('-p', action='store', type=str, default=os.path.join('.','demo.csv'),
                        help='Path to file that data will be saved to.')
    # append
    parser.add_argument('-a', action=argparse.BooleanOptionalAction, type=bool, default=False,
                        help='True to append to file passed, False to write new file.')

    return validate_args(parser.parse_args())

def validate_args(args):
    '''
    Validate arguments based on special conditions per argument.
    '''

    args = {
        'category' : args.c,
        'format' : args.f.lower(),
        'limit' : args.l,
        'file' : args.p,
        'append' : args.a,
    }

    # category
    if args['category'] < 0 or args['category'] > 38:
        sys.exit('Invalid "category" argument:\nMust be between 1 and 38 (based on categories_list.txt).')

    # format
    formats = ['csv', 'jl', 'json']
    if args['format'] not in formats:
        sys.exit('Invalid "format" argument:\nMust be one of {}.'.format(args['formats']))

    # limit
    if args['limit'] > 100 or args['limit'] <= 0:
        sys.exit('Invalid "limit" argument; must be between 1 and 100, not {}'.format(args['limit']))

    # file
    file_format = os.path.splitext(args['file'])[1].replace('.','')

    if file_format not in formats:
        sys.exit('Invalid file format: {}\nMust be one of {}.'.format(file_format, formats))

    if file_format != args['format'] and args['format'] != 'csv':
        sys.exit('Different file formats specified in "format" and "file" argument.')

    # append
    # no need for any validation
    return args

if __name__ == '__main__':

    # default values are incorporated into parse_from_cli
    # read input
    args = parse_from_cli()
    # debug only
    # print(args)

    # create a CrawlerProcess
    settings = get_project_settings()
    FEEDS = {
        args['file'] : {
            'format' : args['format'],
            'overwrite' : args['append'],
        }
    }
    settings.set('FEEDS', FEEDS)
    process = CrawlerProcess(settings)

    # create url
    category = categories[args['category']]
    url = 'https://www.amazon.com/gp/movers-and-shakers/{}'.format(category)

    # set AmazonSpider to crawl with given start_urls
    process.crawl(AmazonSpider, start_urls=[url], limit=args['limit'])

    # begin crawling
    process.start()
