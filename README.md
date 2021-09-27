# AmazonScrape

## What is AmazonScrape
AmazonScrape is a command line program used for scraping data from different categories in Amazon's Movers & Shakers.

## Data Scraped
AmazonScrape will iterate through all of the specified category's items and collect the following data about each product (if available):

 * Name
 * Sales Rank
 * Percentage of increase of Sales Rank
 * Minimum Price
 * Maximum Price
 * Product's Page URL
 * Product's Image URL

## How it Works
AmazonScrape uses a scrapy backend to scrape data from product listings and product pages. AmazonScrape
bypasses CAPTCHA-protected product pages by using User Agents when accessing them.
The data is then written to a csv, json or jl (json lines) file.

## How to Setup

### Prerequisites
    Python 3
    pip3 or pip

   Running AmazonScrape.py for the first time will install any needed packages that are not already installed.

To setup AmazonScrape just clone this repository and change the permissions for the AmazonScrape.py file to make it executable.

    git clone https://github.com/yiannisha/AmazonScrape-2.0.git

    sudo chmod +x AmazonScrape-2.0/AmazonScrape.py
    #The above step is required only for Linux and macOS.

## How to Use
To use AmazonScrape execute the AmazonScrape.py file with all the parameters passed.

    path/AmazonScrape-2.0/AmazonScrape.py -c 22 -f json -l 15 -p ./demo.json -a

AmazonScrape.py options:
* "-c" : Category of Amazon's Movers&Shakers to scrape. (required) (must be chosen based <a href="https://github.com/yiannisha/AmazonScrape-2.0/blob/main/category_list.txt">category_list.txt</a>)
* "-f" : File format to be saved as. (default = csv) (must be one of: csv, jl, json)
* "-l" : Limit of results to return. (default = 100 (max))
* "-p" : Path to output file. (default = ./demo.csv)
* "-a" : Overwrite output file. (default = False)
