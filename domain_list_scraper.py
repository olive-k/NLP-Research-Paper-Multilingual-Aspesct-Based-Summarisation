import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import urllib.request
import json
import time


'''
Runs depth first search of the Categories page of Wikipedia
'''

domain_list = []


def get_domain_list(domain_url):
    http_request = requests.get(domain_url)
    subcats_soup = BeautifulSoup(http_request, 'html.parser').findAll('div',{'id':'mw-subcategories'})[0].findAll('div',{'class':'mw-category-group'})
    pages_soup = BeautifulSoup(http_request, 'html.parser').findAll('div',{'id':'mw-pages'})[0]
    if subcats_soup:
        for subcats in subcats_soup:
            subcat_soup = subcats.findAll('li')
            for subcat in subcat_soup:
                anchor = subcat.find('a', href = True)
                get_domain_list(anchor['href'])
    if pages_soup:
        for pages in pages_soup.findAll('ul'):
            for page in pages.findAll('li'):
                domain_list.append(page.find('a', href = True)['title'])


def save_domain_list(domain, domain_list):
    with open('data/domains/'+domain+'.json', 'w') as fp:
        json.dump(domain_list, fp)


if __name__ == '__main__':
    main_domain_url = 'https://en.wikipedia.org/wiki/Category:Sports'
    domain = 'sports'
    get_domain_list(main_domain_url)
    print(domain_list)
    save_domain_list(domain, domain_list)