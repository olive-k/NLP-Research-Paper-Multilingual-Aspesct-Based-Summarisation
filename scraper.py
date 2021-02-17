import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import urllib.request, json 

def run():
    page_url = "https://en.wikipedia.org/wiki/Paris"
    page_title = "paris"
    sections_query = "https://en.wikipedia.org/w/api.php?action=parse&page=" + page_title + "&format=json&prop=sections"
    references_query = "https://en.wikipedia.org/w/api.php?action=parse&page=" + page_title + "&format=json&prop=externallinks"
    text_query = "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&titles=" + page_title + "&format=json&exsectionformat=wiki"
    results = []
    result = {}

    with urllib.request.urlopen(sections_query) as url:
        sections_data = json.loads(url.read().decode())['parse']['sections']
        print(sections_data)
    
    with urllib.request.urlopen(references_query) as url:
        references_data = json.loads(url.read().decode())['parse']['externallinks']
        print(references_data)
    
    with urllib.request.urlopen(text_query) as url:
        text_data = json.loads(url.read().decode())['query']['pages']
        text_data = text_data[next(iter(text_data))]['extract']
        print(text_data)
    
    archived_url = "https://web.archive.org/web/20190330170311/https://www.telegraph.co.uk/travel/city-breaks/most-expensive-and-cheapest-cities-2018/"
    http_request = requests.get(archived_url).text
    print("get worked!!")
    soup = BeautifulSoup(http_request, 'html.parser').findAll('div',class_ = 'component-content')
    print(len(soup))
    print(soup[0].prettify())


if __name__ == '__main__':
    run()